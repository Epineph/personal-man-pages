"""Preview one exported document on localhost, without sharing its directory."""

from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import sys
import webbrowser


class HelpHandler(BaseHTTPRequestHandler):
  def __init__(self, *args, document: Path, **kwargs):
    self.document = document
    super().__init__(*args, **kwargs)

  def log_message(self, format: str, *args) -> None:
    return

  def deliver(self, head: bool = False) -> None:
    if urlsplit(self.path).path not in {"/", "/help.html"}:
      self.send_error(404, "Only this help document is available.")
      return
    try:
      data = self.document.read_bytes()
    except OSError:
      self.send_error(404, "Help document is unavailable.")
      return
    self.send_response(200)
    self.send_header("Content-Type", "text/html; charset=utf-8")
    self.send_header("Content-Length", str(len(data)))
    self.send_header("Cache-Control", "no-store")
    self.end_headers()
    if not head:
      self.wfile.write(data)

  def do_GET(self) -> None:
    self.deliver()

  def do_HEAD(self) -> None:
    self.deliver(head=True)


def serve_html(document: Path, port: int, open_browser: bool) -> int:
  handler = partial(HelpHandler, document=document)
  with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
    actual_port = server.server_address[1]
    url = f"http://127.0.0.1:{actual_port}/help.html"
    print(
      f"Serving {url}\nPress Ctrl-C to stop; the exported file remains.",
      flush=True,
    )
    if open_browser:
      if not webbrowser.open(url):
        print(f"pman: Open {url} in your browser.", file=sys.stderr)
    try:
      server.serve_forever()
    except KeyboardInterrupt:
      return 0
  return 0
