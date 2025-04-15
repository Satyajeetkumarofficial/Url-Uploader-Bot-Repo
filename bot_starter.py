
# bot_starter.py

import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Start dummy HTTP server on port 8080
def run_web():
    server = HTTPServer(("", 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

# Start the Telegram bot
from bot import *
