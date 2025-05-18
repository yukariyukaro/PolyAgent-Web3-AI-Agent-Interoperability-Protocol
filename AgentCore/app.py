# app.py
import time
from flask import Flask, request, stream_with_context,Response
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# import agent
from AgentCore.crypto_society import get_crypto_agent_data

app = Flask(__name__)

# 跨域
CORS(app)

class StreamToQueue:
    def write(self, msg):
        # if msg.strip():
        print(msg)
        yield msg
    def flush(self):
        pass

@app.route("/polyPost", methods=["POST"])
def run_agent():
    data = request.get_json()
    message = data.get('message', '') if data else ''
    return Response(stream_with_context(get_crypto_agent_data(message)), mimetype='text/plain')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
