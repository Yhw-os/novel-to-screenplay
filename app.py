from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许前端跨域调用

# 创建上传文件夹
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 测试接口：前端用来检查服务器是否活着
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"status": "ok", "message": "服务器运行中"})

# 启动服务器
if __name__ == '__main__':
    app.run(debug=True, port=5000)