"""
This module provides a way to get data from ClassFinder.
This is not meant to be used with web applications, but rather for scripts that need to get data from ClassFinder, as this will run its own flask server to get credentials.
"""
import threading
from flask import Flask, request, jsonify
import webbrowser
import requests
import time
import logging

app = Flask(__name__)
ntoken = None

def get_available_scopes():
    req = requests.get("https://class.trey7658.com/api/v2/scopes")
    if req.status_code == 200:
        return req.json()['scopes']
    logging.error("Failed to fetch scopes: %s - %s", req.status_code, req.text)
    return {}

def get_token(scopes: list = [], openbrowser: bool=True, port: int = 5000) -> str:
    global ntoken
    ntoken = None
    if openbrowser:
        webbrowser.open(f"https://class.trey7658.com/auth?redirect_url=http://localhost:{str(port)}/callback&scopes=" + ",".join(scopes))
    else:
        logging.info("Please open the following URL in your browser: https://class.trey7658.com/auth?redirect_url=http://localhost:%s/callback&scopes=%s", str(port), ",".join(scopes))
    logging.info("Waiting for token...")
    server_thread = threading.Thread(target=run_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()
    while ntoken is None:
        time.sleep(0.1)
    return ntoken

def run_server(port: int = 5000):
    global ntoken
    logging.info("Starting callback server on port %s", port)
    app.run(port=port, debug=False, use_reloader=False)

@app.route('/callback', methods=['GET'])
def callback():
    global ntoken
    code = request.args.get('token')
    if code:
        ntoken = code
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error", "message": "No token received"}), 400