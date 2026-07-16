"""Squad — Web Server. Wraps the Python terminal game as a web application."""
import sys, os, re, subprocess, threading, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask, request

app = Flask(__name__)

class GameSession:
    """Manages a single game subprocess with stdin/stdout."""
    
    def __init__(self):
        self.proc = None
        self.output = ""
        self.lock = threading.Lock()
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
        
        self.running = True
        self.reader = threading.Thread(target=self._reader, daemon=True)
        self.reader.start()
        time.sleep(0.3)
    
    def _reader(self):
        strip_ansi = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\][^\x1b]*\x1b\\|\x1b[^[]').sub
        while self.running and self.proc and self.proc.stdout:
            try:
                line = self.proc.stdout.readline()
                if not line:
                    break
                clean = strip_ansi('', line)
                with self.lock:
                    self.output += clean
            except (ValueError, OSError):
                break
    
    def send_input(self, text: str):
        if self.proc and self.proc.stdin:
            self.proc.stdin.write(text + '\n')
            self.proc.stdin.flush()
            time.sleep(0.15)
    
    def get_output(self) -> str:
        with self.lock:
            return self.output
    
    def close(self):
        self.running = False
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except: pass
            self.proc = None


_game = None
def get_game():
    global _game
    if _game is None:
        _game = GameSession()
    return _game


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>SQUAD</title>
<link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;background:#0d0a18;color:#f0ecf8;font-family:'VT323',monospace;font-size:18px;overflow:hidden}
#t{width:100%;height:calc(100% - 48px);padding:12px;padding-top:32px;overflow-y:auto;white-space:pre-wrap;word-wrap:break-word;font-family:'VT323',monospace;font-size:15px;line-height:1.3;color:#39ff14;background:#0d0a18}
#t .b{font-weight:bold}#t .d{color:#9a8ab0}#t .g{color:#39ff14}#t .y{color:#ffd700}#t .r{color:#ff3344}#t .c{color:#00ccff}#t .m{color:#ff00ff}
#i-l{display:flex;align-items:center;padding:6px 12px;background:#161120;border-top:1px solid #3d2d5c;height:48px;position:fixed;bottom:0;left:0;right:0}
#i-l input{flex:1;background:transparent;border:none;color:#39ff14;font-family:'VT323',monospace;font-size:18px;outline:none}
#i-l input::placeholder{color:#3d2d5c}
#s{position:fixed;top:0;left:0;right:0;height:28px;background:#161120;border-bottom:1px solid #3d2d5c;padding:4px 12px;font-size:14px;color:#9a8ab0;display:flex;justify-content:space-between;z-index:10}
@media(max-width:600px){#t{font-size:13px;padding:6px;padding-top:28px}}
</style>
</head>
<body>
<div id=s><span>SQUAD</span><span id=st>Connecting...</span></div>
<div id=t></div>
<div id=i-l><input type=text id=inp autofocus placeholder="Type here..."></div>
<script>
var t=document.getElementById('t'),inp=document.getElementById('inp'),st=document.getElementById('st');
var buf='';
function fix(s){
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\[bold\]/g,'<b>').replace(/\[\/bold\]/g,'</b>')
    .replace(/\[dim\]/g,'<span class=d>').replace(/\[\/dim\]/g,'</span>')
    .replace(/\[green\]/g,'<span class=g>').replace(/\[\/green\]/g,'</span>')
    .replace(/\[yellow\]/g,'<span class=y>').replace(/\[\/yellow\]/g,'</span>')
    .replace(/\[red\]/g,'<span class=r>').replace(/\[\/red\]/g,'</span>')
    .replace(/\[cyan\]/g,'<span class=c>').replace(/\[\/cyan\]/g,'</span>')
    .replace(/\[magenta\]/g,'<span class=m>').replace(/\[\/magenta\]/g,'</span>');
}
function poll(){
  fetch('/output').then(function(r){return r.text()}).then(function(text){
    if(text!==buf){buf=text;t.innerHTML=fix(text);t.scrollTop=t.scrollHeight;}
    st.textContent='Connected';
  }).catch(function(){st.textContent='Disconnected'});
}
setInterval(poll,500);poll();
inp.addEventListener('keydown',function(e){
  if(e.key==='Enter'){
    var v=this.value;this.value='';
    fetch('/input',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'text='+encodeURIComponent(v)})
    .then(function(){setTimeout(poll,300)});
  }
});
document.addEventListener('click',function(){inp.focus()});
</script>
</body>
</html>"""


@app.route('/')
def index():
    return HTML

@app.route('/output')
def get_output():
    return get_game().get_output()

@app.route('/input', methods=['POST'])
def send_input():
    get_game().send_input(request.form.get('text', ''))
    return 'ok'

@app.route('/reset', methods=['POST'])
def reset_game():
    global _game
    if _game:
        _game.close()
    _game = None
    return 'ok'


if __name__ == '__main__':
    print("Squad web server on http://0.0.0.0:8081")
    app.run(host='0.0.0.0', port=8081, debug=False, threaded=True)
