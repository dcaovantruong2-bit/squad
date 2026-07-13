"""Squad — Web Server
Wraps the Python terminal game as a web application.
Uses subprocess with stdin/stdout — no PTY complexity.
"""
import sys, os, re, subprocess, threading, time, signal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string, request

app = Flask(__name__)

# ─── Game Process Management ───────────────────────────────────────────

class GameSession:
    """Manages a single game subprocess with stdin/stdout."""
    
    def __init__(self):
        self.proc = None
        self.output = ""
        self.lock = threading.Lock()
        self.buffer = []
        self._start_game()
    
    def _start_game(self):
        game_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        python = os.path.join(game_dir, '.venv', 'bin', 'python3')
        main = os.path.join(game_dir, 'main.py')
        
        self.proc = subprocess.Popen(
            [python, main],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=game_dir,
            text=True,
            bufsize=0,
        )
        
        # Start reader thread
        self.running = True
        self.reader = threading.Thread(target=self._reader, daemon=True)
        self.reader.start()
        
        # Wait for initial output
        time.sleep(0.3)
    
    def _reader(self):
        """Background thread: read all output from the process."""
        while self.running and self.proc and self.proc.stdout:
            try:
                line = self.proc.stdout.readline()
                if not line:
                    break
                with self.lock:
                    # Strip ANSI codes
                    clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line)
                    clean = re.sub(r'\x1b\][0-9;]*[^\x1b]*\x1b\\', '', clean)
                    clean = re.sub(r'\x1b[^[]', '', clean)
                    self.output += clean
                    self.buffer.append(clean)
                    # Keep buffer manageable
                    if len(self.buffer) > 500:
                        self.buffer = self.buffer[-300:]
            except (ValueError, OSError):
                break
    
    def send_input(self, text: str):
        """Send text to the game process."""
        if self.proc and self.proc.stdin:
            self.proc.stdin.write(text + '\n')
            self.proc.stdin.flush()
            time.sleep(0.1)  # Let the game process the input
    
    def get_output(self) -> str:
        """Get all accumulated output."""
        with self.lock:
            return self.output
    
    def close(self):
        """Kill the game process."""
        self.running = False
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except (subprocess.TimeoutExpired, OSError):
                try:
                    self.proc.kill()
                    self.proc.wait(timeout=1)
                except OSError:
                    pass
            self.proc = None


# Global game session
_game = None

def get_game():
    global _game
    if _game is None:
        _game = GameSession()
    return _game


# ─── Routes ────────────────────────────────────────────────────────────

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>SQUAD — Football Card Roguelike</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; height: 100%; background: #0d0a18; color: #f0ecf8; font-family: 'VT323', monospace; font-size: 18px; overflow: hidden; }
#terminal {
  width: 100%; height: calc(100% - 48px); padding: 12px; padding-top: 32px;
  overflow-y: auto; white-space: pre-wrap; word-wrap: break-word;
  font-family: 'VT323', monospace; font-size: 15px; line-height: 1.3;
  color: #39ff14; background: #0d0a18; scroll-behavior: smooth;
}
#terminal .b { font-weight: bold; }
#terminal .d { color: #9a8ab0; }
#terminal .g { color: #39ff14; }
#terminal .y { color: #ffd700; }
#terminal .r { color: #ff3344; }
#terminal .c { color: #00ccff; }
#terminal .m { color: #ff00ff; }
#input-line {
  display: flex; align-items: center; padding: 6px 12px;
  background: #161120; border-top: 1px solid #3d2d5c; height: 48px;
  position: fixed; bottom: 0; left: 0; right: 0;
}
#input-line input {
  flex: 1; background: transparent; border: none;
  color: #39ff14; font-family: 'VT323', monospace; font-size: 18px; outline: none;
}
#input-line input::placeholder { color: #3d2d5c; }
#status-bar {
  position: fixed; top: 0; left: 0; right: 0; height: 28px;
  background: #161120; border-bottom: 1px solid #3d2d5c;
  padding: 4px 12px; font-size: 14px; color: #9a8ab0;
  display: flex; justify-content: space-between; z-index: 10;
}
@media (max-width: 600px) {
  #terminal { font-size: 13px; padding: 6px; padding-top: 28px; }
}
</style>
</head>
<body>
<div id="status-bar"><span>SQUAD</span><span id="s">Connected</span></div>
<div id="terminal"></div>
<div id="input-line"><input type="text" id="i" autofocus placeholder="Type command..."></div>
<script>
const t=document.getElementById('terminal'),i=document.getElementById('i'),s=document.getElementById('s');
let buf='';
function styleRich(text){
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/&#x5b;bold&#x5d;/g,'<b>').replace(/&#x5b;\/bold&#x5d;/g,'</b>')
    .replace(/&#x5b;dim&#x5d;/g,'<span class="d">').replace(/&#x5b;\/dim&#x5d;/g,'</span>')
    .replace(/&#x5b;green&#x5d;/g,'<span class="g">').replace(/&#x5b;\/green&#x5d;/g,'</span>')
    .replace(/&#x5b;yellow&#x5d;/g,'<span class="y">').replace(/&#x5b;\/yellow&#x5d;/g,'</span>')
    .replace(/&#x5b;red&#x5d;/g,'<span class="r">').replace(/&#x5b;\/red&#x5d;/g,'</span>')
    .replace(/&#x5b;cyan&#x5d;/g,'<span class="c">').replace(/&#x5b;\/cyan&#x5d;/g,'</span>')
    .replace(/&#x5b;magenta&#x5d;/g,'<span class="m">').replace(/&#x5b;\/magenta&#x5d;/g,'</span>');
}
function poll(){
  fetch('/output').then(r=>r.text()).then(text=>{
    if(text!==buf){buf=text;t.innerHTML=styleRich(text);t.scrollTop=t.scrollHeight;}
    s.textContent='Connected';
  }).catch(()=>s.textContent='Disconnected');
}
setInterval(poll,400);poll();
i.addEventListener('keydown',function(e){
  if(e.key==='Enter'){
    const v=this.value;this.value='';
    fetch('/input',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'text='+encodeURIComponent(v)})
    .then(()=>setTimeout(poll,300));
  }
});
document.addEventListener('click',()=>i.focus());
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/output')
def get_output():
    game = get_game()
    return game.get_output()

@app.route('/input', methods=['POST'])
def send_input():
    text = request.form.get('text', '')
    game = get_game()
    game.send_input(text)
    return 'ok'

@app.route('/reset', methods=['POST'])
def reset_game():
    global _game
    if _game:
        _game.close()
    _game = GameSession()
    return 'ok'


if __name__ == '__main__':
    print("Squad web server on http://0.0.0.0:8081")
    app.run(host='0.0.0.0', port=8081, debug=False, threaded=True)
