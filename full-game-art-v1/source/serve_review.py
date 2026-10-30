from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
R=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(R)))
print(f'http://127.0.0.1:{server.server_port}/previews/playback.html',flush=True)
server.serve_forever()
