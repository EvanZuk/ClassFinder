from waitress import serve
from app import app
from app.utilities.env import devmode
import signal
import sys

def signal_handler(sig, frame):
    print("Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if devmode:
    print("Running in dev mode")
else:
    print("Running in production mode")

if __name__ == "__main__":
    if devmode:
        app.run(host="0.0.0.0", port=5200, debug=True)
    else:
        serve(app, host="0.0.0.0", port=7842)
