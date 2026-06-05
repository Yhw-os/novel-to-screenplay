# 剧本 YAML Schema 设计文档

## 1. 为什么用 YAML？

| 维度 | YAML | JSON | 说明 |
|------|------|------|------|
| 人类可读 | ★★★ | ★★ | 作者可直接编辑，支持注释 |
| 多行文本 | ★★★ | ★ | 对话内容用 `|` 保留换行 |
| 与 AI 配合 | ★★★ | ★★ | LLM 输出 YAML 比 JSON 更不易出错 |

## 2. 核心结构设计

screenplay
├── metadata          # 剧本元信息（标题、来源章节）
├── dramatis_personae # 角色总表（id/name/description）
└── scenes            # 场景列表
├── heading           # 场景标题（INT/EXT, 地点, 时间）
├── synopsis          # 场景简介
└── elements          # 场景内元素
├── type              # action/dialogue/voiceover/sound_effect
├── content           # 内容
├── character_id      # 角色引用
└── notes
├── confidence        # AI 置信度 0.0-1.0
└── adaptation_note   # 改编说明


## 3. 关键设计决策

### 3.1 confidence 字段
- **原因**：AI 转换存在不确定性，需要让作者知道哪里需要人工复核
- **阈值**：<< 0.8 标红，前端可视化时突出显示

### 3.2 dramatis_personae 独立角色表
- **原因**：小说里"林深/林总/深哥"可能是同一个人，AI 容易重复创建
- **作用**：统一角色管理，支持编辑后全局同步更新

### 3.3 元素原子化
- 小说文本是连续流，剧本是离散指令
- 同一段原文可能混合动作+对话+心理，必须拆分才能用于拍摄

## 4. 示例

见 `schema/examples/example_short.yaml`