# Trilium2Anki

? 自动将 Trilium 笔记转换为 Anki 记忆卡片的工具

## ? 功能特性

- ? **自动同步**：自动从 Trilium 获取每日学习笔记
- ? **智能生成**：使用 LLM（DeepSeek/OpenAI）生成高质量问答对
- ? **灵活模式**：支持三种笔记获取方式（日历笔记/搜索/固定文档）
- ? **直接导入**：通过 AnkiConnect 自动添加到 Anki
- ?? **可配置**：支持自定义卡片数量、难度、标签等

## ? 系统要求

- Python 3.8+
- Trilium Notes（需开启 ETAPI）
- Anki（需安装 AnkiConnect 插件）
- LLM API（支持 OpenAI 兼容接口）

## ? 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置文件

复制配置模板并编辑：

```bash
cp config.yaml.example config.yaml
```

编辑 `config.yaml`，填入你的配置信息：

```yaml
trilium:
  server_url: "http://your-trilium-server:8080"
  api_token: "your_api_token"
  fetch_mode: "calendar"  # 或 search / fixed_note

llm:
  api_base: "https://api.deepseek.com"
  api_key: "sk-your-key"
  model: "deepseek-chat"

anki:
  deck_name: "我的学习"
  model_name: "问答题"
  tags: ["自动生成"]
```

### 3. 准备 Anki

1. 安装 [AnkiConnect](https://ankiweb.net/shared/info/2055492159) 插件
2. 确保 Anki 正在运行
3. 在 Anki 中创建笔记类型 "问答题"，包含字段：
   - 正面（问题）
   - 背面（答案）

### 4. 运行

```bash
python -m src.main
```

或者：

```bash
cd src
python main.py
```

## ? 使用说明

### 三种笔记获取模式

#### 1. Calendar 模式（推荐）

使用 Trilium 的日历笔记功能，自动获取今天的笔记。

```yaml
trilium:
  fetch_mode: "calendar"
```

#### 2. Search 模式

通过搜索关键词查找笔记，支持日期占位符。

```yaml
trilium:
  fetch_mode: "search"
  search_template: "学习笔记 {date}"  # {date} 会被替换为 "2025年11月03日"
```

#### 3. Fixed Note 模式

从一个固定的笔记文档中提取今天的内容（类似语雀文档模式）。

```yaml
trilium:
  fetch_mode: "fixed_note"
  note_id: "your_note_id"  # 笔记需要按日期分段，如 "## 2025年11月03日"
```

### 日期格式支持

Fixed Note 模式支持多种日期格式：

- `2025年11月3日` / `2025年11月03日`
- `2025-11-3` / `2025-11-03`
- `2025/11/3` / `2025/11/03`

### 卡片生成配置

在 `config.yaml` 中可设置卡片数量和难度：

```yaml
generation:
  cards_per_day: 5  # 每天生成的卡片数量（设为 0 则由 LLM 自动决定）
  difficulty: "适中"  # 简单/适中/困难
```

**提示**：将 `cards_per_day` 设为 0 时，LLM 会根据笔记内容的丰富程度自动决定生成卡片的数量（通常 3-10 个）

## ?? 项目结构

```
Trilium2Anki/
├── src/
│   ├── __init__.py
│   ├── main.py              # 主程序入口
│   ├── trilium_fetcher.py   # Trilium API 交互
│   ├── content_parser.py    # 内容解析（HTML/Markdown）
│   ├── llm_generator.py     # LLM 问答生成
│   ├── anki_exporter.py     # Anki 卡片导出
│   └── prompt.py            # LLM 提示词
├── config.yaml.example      # 配置模板
├── requirements.txt         # 依赖列表
└── README.md
```

## ? 技术栈

- **Trilium API**：ETAPI
- **LLM**：OpenAI SDK（兼容 DeepSeek 等）
- **Anki**：AnkiConnect
- **解析**：BeautifulSoup4

## ?? 注意事项

1. **敏感信息**：不要将 `config.yaml` 提交到 Git 仓库
2. **API 配额**：注意 LLM API 的调用次数和费用
3. **重复卡片**：程序会自动跳过重复的卡片（基于内容去重）
4. **Anki 运行**：使用前请确保 Anki 已启动

## ? 常见问题

### 连接 Trilium 失败

- 检查 `server_url` 是否正确
- 确认 Trilium ETAPI 已启用
- 验证 `api_token` 是否有效

### 连接 Anki 失败

- 确认 Anki 正在运行
- 检查 AnkiConnect 插件是否已安装
- 验证端口 8765 未被占用

### LLM 生成失败

- 检查 API 密钥是否正确
- 确认网络连接正常
- 验证 API 配额是否充足

### 找不到今天的笔记

- **Calendar 模式**：确认今天是否有创建日历笔记
- **Search 模式**：检查搜索关键词是否正确
- **Fixed Note 模式**：确认文档中是否有今天的日期标题

## ? 开发计划

- [ ] 支持批量处理历史笔记
- [ ] 添加卡片质量评分
- [ ] 支持图片内容
- [ ] 添加 Web UI 界面
- [ ] 支持更多 LLM 提供商

## ? 贡献

欢迎提交 Issue 和 Pull Request！

## ? 许可证

MIT License

## ? 作者

欢迎交流学习！

---

? 如果这个项目对你有帮助，请给一个 Star！

