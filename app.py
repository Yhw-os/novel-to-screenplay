from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import requests

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ========== 工具函数：解析章节 ==========
def split_chapters(text):
    pattern = r'(第[一二三四五六七八九十百零\d]+章[：:\s]*[^\n]*)'
    parts = re.split(pattern, text)
    chapters = []
    chapter_id = 0
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            title = parts[i].strip()
            content = parts[i+1].strip()
            if len(content) > 20:
                chapters.append({
                    "id": chapter_id,
                    "title": title,
                    "content": content
                })
                chapter_id += 1
    return chapters

# ========== 工具函数：调用 DeepSeek ==========
def call_deepseek(prompt):
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        return None, "错误：没有设置 DEEPSEEK_API_KEY 环境变量"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位专业编剧，擅长将小说转换为剧本YAML格式。只输出YAML，不要任何解释，不要markdown代码块标记。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=data,
            timeout=120
        )
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content'], None
        else:
            return None, f"API返回异常: {result}"
    except Exception as e:
        return None, str(e)

# ========== API 1：测试服务器 ==========
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
    for encoding in ['utf-8', 'gbk', 'gb2312']:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                text = f.read()
            break
        except:
            continue
    
    if not text:
        return jsonify({"error": "无法读取文件"}), 400
    
    chapters = split_chapters(text)
    
    # 兜底：如果没解析到章节，整篇当一章
    if len(chapters) == 0:
        chapters = [{
            "id": 0,
            "title": "全文",
            "content": text[:300] + "..."
        }]
    
    return jsonify({
        "success": True,
        "filename": file.filename,
        "total_chapters": len(chapters),
        "chapters": chapters
    })

# ========== API 3：AI 转换（核心）==========
@app.route('/api/convert', methods=['POST'])
def convert():
    data = request.get_json()
    chapter_ids = data.get('chapter_ids', [])
    filename = data.get('filename', '')
    
    if not chapter_ids:
        return jsonify({"error": "未选择章节"}), 400
    
    # 读取文件
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "文件不存在"}), 404
    
    # 尝试多种编码
    text = ""
    for encoding in ['utf-8', 'gbk', 'gb2312']:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                text = f.read()
            break
        except:
            continue
    
    # 解析章节
    chapters = split_chapters(text)
    if len(chapters) == 0:
        chapters = [{"id": 0, "title": "全文", "content": text}]
    
    # 提取选中的章节
    selected = [ch for ch in chapters if ch['id'] in chapter_ids]
    if len(selected) == 0:
        return jsonify({"error": "选中的章节不存在"}), 400
    
    # 拼接成完整文本
    combined_text = "\n\n".join([
        f"=== {ch['title']} ===\n{ch['content']}" 
        for ch in selected
    ])
    
    # 构建 Prompt
    prompt = f"""请将以下小说章节转换为剧本 YAML 格式。

要求：
1. 输出必须是标准 YAML，不要加 markdown 代码块标记（如 ```yaml）
2. 顶层键为 screenplay
3. 包含 metadata（title, source_chapters）
4. 包含 dramatis_personae（角色列表，每个角色有 id, name, description）
5. 包含 scenes（场景列表），每个 scene 有：
   - heading: location, time_of_day（DAY/NIGHT）
   - synopsis: 场景简介
   - elements: 场景内元素，类型包括 action, dialogue, voiceover, sound_effect
6. 每个 element 包含：
   - type: 元素类型
   - content: 内容
   - character_id: 角色ID（如果是 dialogue/voiceover）
   - notes:
       confidence: 0.0-1.0（AI对转换的自信度）
       adaptation_note: 改编说明
7. 心理描写转为 voiceover（画外音）
8. 环境描写转为 sound_effect 或 action

小说内容：
{combined_text}
"""
    
    # 调用 AI
    yaml_content, error = call_deepseek(prompt)
    if error:
        return jsonify({"error": error}), 500
    
    # 清理 AI 可能加上的 markdown 标记
    yaml_content = yaml_content.strip()
    if yaml_content.startswith('```yaml'):
        yaml_content = yaml_content[7:]
    if yaml_content.startswith('```'):
        yaml_content = yaml_content[3:]
    if yaml_content.endswith('```'):
        yaml_content = yaml_content[:-3]
    yaml_content = yaml_content.strip()
    
    return jsonify({
        "success": True,
        "yaml": yaml_content,
        "selected_chapters": len(selected)
    })
import yaml as pyyaml

@app.route('/api/parse-yaml', methods=['POST'])
def parse_yaml():
    """
    前端把 YAML 字符串发过来，后端解析成 JSON，方便前端渲染卡片
    """
    data = request.get_json()
    yaml_text = data.get('yaml', '')
    
    try:
        parsed = pyyaml.safe_load(yaml_text)
        return jsonify({"success": True, "data": parsed})
    except Exception as e:
        return jsonify({"error": "YAML解析失败: " + str(e)}), 400
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)