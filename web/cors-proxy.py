#!/usr/bin/env python3
"""Simple CORS proxy for OpenDesign: read request, strip Origin, forward, return response."""
import socket, threading, re, sys

TARGET = ('127.0.0.1', 3000)

def handle(client):
    try:
        data = b''
        while True:
            chunk = client.recv(65536)
            if not chunk: break
            data += chunk
            if b'\r\n\r\n' in data: break

        if not data: return

        # Strip Origin and rewrite Host
        text = data.decode('utf-8', errors='replace')
        cleaned = re.sub(r'^Origin:.*\r?\n', '', text, flags=re.MULTILINE)
        cleaned = re.sub(r'^Host:.*\r?\n', 'Host: 127.0.0.1:' + str(TARGET[1]) + '\r\n', cleaned, flags=re.MULTILINE)

        backend = socket.socket()
        backend.settimeout(30)
        backend.connect(TARGET)
        backend.sendall(cleaned.encode('utf-8'))

        # Forward response back
        while True:
            chunk = backend.recv(65536)
            if not chunk: break
            client.sendall(chunk)
    except Exception as e:
        print(f'[proxy] {e}', file=sys.stderr, flush=True)
    finally:
        try: client.close()
        except: pass
        try: backend.close()
        except: pass

server = socket.socket()
server.setsockopt(1, 2, 1)
server.bind(('0.0.0.0', 8082))
server.listen(128)
print('[proxy] ready 0.0.0.0:8082 -> 127.0.0.1:3000', flush=True)
while True:
    c, a = server.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
