from flask import Flask, jsonify
import threading
import time

app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({"status":"pong"}), 200

def run_web():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    while True:
        time.sleep(60)
