# AI 小说转剧本工具

&gt; 七牛云项目比赛作品

## 快速启动

```bash
pip install -r requirements.txt
$env:DEEPSEEK_API_KEY="sk-xxx"  # Windows
python app.py
访问 http://localhost:5000/static/index.html

 功能
📤 上传 .txt 小说，自动解析章节（支持"第一章"等中文格式）
🤖 选择 3+ 章节，DeepSeek AI 自动转换为剧本 YAML
🎬 可视化预览：场景卡片、角色表、元素类型颜色区分
⚠️ 低置信度标红：AI 不确定的转换自动警告
✏️ 角色编辑：修改角色名后，所有场景引用自动同步
⬇️ 双格式导出：YAML（结构化）+ TXT（标准剧本格式）

技术栈
后端：Flask + DeepSeek API
前端：原生 HTML/JS
格式：YAML

项目结构
novel-to-screenplay/
├── app.py                 # Flask 后端
├── static/index.html      # 前端页面
├── docs/                  # 设计文档
└── schema/                # YAML Schema + 示例

演示视频




