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

def generate():
    yield "开始处理...\n"
    # for i in range(5):
    #     yield f"第 {i+1} 步完成\n"

    yield "全部完成！\n"

class StreamToQueue:
    def write(self, msg):
        # if msg.strip():
        print(msg)
        yield msg
    def flush(self):
        pass

@app.route("/polyPost", methods=["POST"])
def run_agent():
    # def generate():
    #     result = get_crypto_agent_data()
    #     for char in result["msg"]:
    #         yield char
    #         time.sleep(0.02)  # 模拟流式

    # return Response(stream_with_context(generate()), mimetype='text/plain')
    data = request.get_json()
    message = data.get('message', '') if data else ''
    return Response(stream_with_context(get_crypto_agent_data(message)), mimetype='text/plain')

    # return Response(json_stream(), mimetype='application/json')
    # user_input = request.json.get()
    # 1.查询市场信息
    # result = get_crypto_agent_data()
    #
    # # 2.根据市场信息生成教育策略
    #
    # # 3.根据交易策略掉用hummingbot
    #
    # # 4.hummingbot执行交易
    #
    # # 5.返回执行成功信息
    #
    # # 你可以在这里调用 subprocess 启动 Hummingbot 等
    # print("===========================================================")
    # print("Received:", result)
    # #
    # return jsonify({"result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
