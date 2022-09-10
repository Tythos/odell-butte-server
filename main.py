"""
"""

import os
import time
import flask
from gevent import pywsgi
from geventwebsocket import handler
import flask_sockets

SERVER_NAME = "odell-butte-server"
APP = flask.Flask(SERVER_NAME)
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))
WS_POOL = []
MOD_PATH, _ = os.path.split(os.path.abspath(__file__))
SOCKETS = flask_sockets.Sockets(APP)

@APP.route("/")
def index():
    """
    HTTP GET will return an HTML file for testing server behavior
    """
    return flask.send_file(MOD_PATH + "/index.html")

def onWsMessage(ws, msg):
    """
    Basic broadcast operation relays any message to all other websocket
    connections in pool.
    """
    for w in WS_POOL:
        if not w is ws and not w.closed:
            w.send(msg)

@SOCKETS.route("/")
def socket(ws):
    """
    When a new WebSocket connection is made, it is added to the pool. When
    messages from that connection are received, they are broadcast to all other
    connections in the pool.
    """
    global WS_POOL
    WS_POOL.append(ws)
    while not ws.closed:
        msg = ws.receive() # BLOCKING
        if msg is not None:
            onWsMessage(ws, msg)
        time.sleep(0.1)
    WS_POOL.remove(ws)

def main():
    """
    Starts the Flask server with a WebSocketHandler extension.
    """
    print("Serving %s at %s:%u..." % (SERVER_NAME, SERVER_HOST, SERVER_PORT))
    try:
        pywsgi.WSGIServer((SERVER_HOST, SERVER_PORT), APP, **{
            "handler_class": handler.WebSocketHandler
        }).serve_forever() # BLOCKING
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
