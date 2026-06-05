from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ========== 工具函数：解析章节 ==========
def split_chapters(text):
    """
    用多种格式匹配章节标题，支持：
    第一章 / 第1章 / 第01章 / CHAPTER 1 等
    """
    # 先尝试中文数字格式
    pattern = r'(第[一二三四五六七八九十百零\d]+章[^\n]*)'
    parts = re.split(pattern, text)
    
    # 如果没匹配到，尝试"第1章"纯数字格式
    if len(parts) <= 2:
        pattern = r'(第\s*\d+\s*章[^\n]*)'
        parts = re.split(pattern, text)
    
    # 还是没匹配到，尝试"1." 或 "1、" 开头
    if len(parts) <= 2:
        pattern = r'(\d+[\s\.、．][^\n]{0,30})'
        parts = re.split(pattern, text)
    
    chapters = []
    chapter_id = 0
    
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            title = parts[i].strip()
            content = parts[i+1].strip()
            # 调试：打印看到底匹配到了什么
            print(f"DEBUG: 匹配到标题 [{title}], 内容长度 {len(content)}")
            if len(content) > 20:  # 降低阈值
                chapters.append({
                    "id": chapter_id,
                    "title": title,
                    "content": content[:200] + "..."
                })
                chapter_id += 1
    
    return chapters

# ========== API 1：测试 ==========
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"status": "ok", "message": "服务器运行中"})

# ========== API 2：上传文件 ==========
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "没有文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # 尝试多种编码读取
    text = ""
    for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                text = f.read()
            break
        except:
            continue
    
    if not text:
        return jsonify({"error": "无法读取文件编码"}), 400
    
    chapters = split_chapters(text)
    
    # 如果还是0章，把整个文本当一章返回（兜底）
    if len(chapters) == 0:
        chapters = [{
            "id": 0,
            "title": "全文（未检测到章节标题）",
            "content": text[:300] + "..."
        }]
    
    return jsonify({
        "success": True,
        "filename": file.filename,
        "total_chapters": len(chapters),
        "chapters": chapters
    })
if __name__ == '__main__':
    app.run(debug=True, port=5000)