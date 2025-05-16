# Fast-Langdetect API

[![语言检测API](https://img.shields.io/badge/API-在线服务-brightgreen)](https://langdetect.liuhetian.work)

## 🚀 项目简介

Fast-Langdetect API是一个高效的多语言检测服务，基于`fast-langdetect`库构建，并提供了多种语言检测策略。它支持多种语言的检测，包括中文（简体与繁体）、英语、法语、德语等多种语言，并且可以根据需要选择不同的检测模型。

### ✨ 特色功能

- 🔍 支持三种检测模式：fast-langdetect（快速模式）、LLM（大模型模式）和auto（混合模式）
- 🌐 支持20+种主流语言的检测
- 📊 自动记录检测历史，方便数据分析
- 🔄 智能区分简体中文和繁体中文
- ⚡ 高性能设计，支持快速响应
- 🐳 Docker部署支持，便于生产环境使用

## 🛠️ 技术栈

- FastAPI - 高性能Web框架
- SQLModel - 数据库ORM
- fast-langdetect - 语言检测核心库
- LangChain - 大模型调用框架
- OpenAI模型 - 提供高准确度语言检测

## 🔧 安装与部署

### 使用Docker部署（推荐）

```bash
# 拉取代码
git clone https://github.com/yourusername/fast-langdetect-api.git
cd fast-langdetect-api

# 构建Docker镜像
docker build -t fast-langdetect-api .

# 运行容器
docker run -d -p 8000:8000 \
  -e LLM_MODEL=gpt-4o-mini \
  -e OPENAI_API_KEY=your_openai_api_key \
  -v $(pwd)/volume:/volume \
  --name langdetect-api fast-langdetect-api
```

### 本地开发环境

```bash
# 克隆仓库
git clone https://github.com/yourusername/fast-langdetect-api.git
cd fast-langdetect-api
```

使用uv(推荐)
```bash 
uv sync
OPENAI_API_KEY=sk-5jCOeVQCZoDyLwBMf_9sowi_DCrQ9DabYGWfoMwHy8W04BjEei8N54_3qgw LLM_MODEL=deepseek-chat  DB_DIR=volume/dbs uv run main.py
```

否则使用：
```bash
# 创建虚拟环境（需要Python 3.12+）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .

# 运行开发服务器
uvicorn main:app --reload
```

## 📚 API使用指南

### 语言检测

**POST** `/detect`

请求示例：

```json
{
  "text": "这是一段需要检测语言的文本",
  "model": "auto",
  "fast_langdetect_min_score": 0.5,
  "trans_code": true
}
```

参数说明：

- `text`：必填，要检测的文本内容
- `model`：可选，检测模型选择
  - `fast-langdetect`：使用fast-langdetect模型（默认）
  - `auto`：先用fast-langdetect检测，若置信度低于阈值则使用LLM
  - `llm`：直接使用LLM检测
- `fast_langdetect_min_score`：可选，fast-langdetect最小置信度（0.0-1.0），低于此值时auto模式会使用LLM
- `trans_code`：可选，是否转换语言代码为标准格式
- `use_project`：可选，项目标识，用于数据分析

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "lang_code": "cn",
    "lang_cn": "简体中文",
    "score": 0.92,
    "use_model": "fast-langdetect",
    "time_spend": 0.015,
    "traces": ["使用fast-langdetect模型进行检测", "检测结果: {...}"],
    "created_at": "2023-05-20T15:30:45.123456"
  }
}
```

### 其他API

- **GET** `/` - 服务健康检查
- **GET** `/recent_fails` - 获取最近检测失败的记录
- **DELETE** `/delete/month_ago` - 删除一个月前的历史记录

## 📋 支持的语言

| 代码 | 语言名称 |
|------|----------|
| cn   | 简体中文 |
| zh   | 繁体中文 |
| en   | 英语 |
| fr   | 法语 |
| de   | 德语 |
| po   | 葡萄牙语 |
| id   | 印尼语 |
| th   | 泰语 |
| sp   | 西班牙语 |
| ru   | 俄语 |
| tr   | 土耳其语 |
| vi   | 越南语 |
| it   | 意大利语 |
| ar   | 阿拉伯语 |
| jp   | 日语 |
| kr   | 韩语 |
| ms   | 马来语 |
| pl   | 波兰语 |
| nl   | 荷兰语 |
| fa   | 波斯语 |
| ro   | 罗马尼亚语 |
| uk   | 乌克兰语 |
| tl   | 菲律宾语 |

## 📊 使用场景

1. **内容审核系统**：识别用户输入的语言类型，进行针对性的内容审核
2. **多语言客服系统**：自动识别用户询问的语言，分配给对应语种的客服人员
3. **跨语言搜索引擎**：根据检测到的语言选择合适的搜索算法和索引
4. **国际化应用**：根据用户输入的语言自动切换界面语言
5. **数据分析**：分析用户内容的语言分布，了解用户群体构成

## 🔗 在线体验

访问 [https://langdetect.liuhetian.work/docs](https://langdetect.liuhetian.work/docs) 体验API并阅读完整文档

## 📝 许可证

[MIT License](LICENSE)
