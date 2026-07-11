#!/usr/bin/env python3
"""Simple threaded HTTP proxy that forwards to localhost:3000 with CORS support."""
import socket, threading, sys, os

TARGET = ('127.0.0.1', 3000)

def pipe(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data: break
            dst.sendall(data)
    except: pass
    finally:
        try: src.shutdown(socket.SHUT_RDWR)
        except: pass
        try: dst.shutdown(socket.SHUT_RDWR)
        except: pass

def handle(client, addr):
    try:
        backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend.connect(TARGET)
        # Forward bidirectionally
        t1 = threading.Thread(target=pipe, args=(client, backend), daemon=True)
        t2 = threading.Thread(target=pipe, args=(backend, client), daemon=True)
        t1.start(); t2.start()
        t1.join(); t2.join()
    except Exception as e:
        pass
    finally:
        try: client.close()
        except: pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 8082))
server.listen(128)
print('Proxy running on port 8082 -> 127.0.0.1:3000', flush=True)

while True:
    client, addr = server.accept()
    threading.Thread(target=handle, args=(client, addr), daemon=True).start()
