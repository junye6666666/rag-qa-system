# 📚 RAG 知识库问答系统

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-1c3c3c?logo=langchain)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-16%20passed-brightgreen)](tests/)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker)](Dockerfile)

</div>

---

## 🎯 项目简介

基于 **检索增强生成（RAG）** 的智能知识库问答系统。上传文档 → 自动理解内容 → 精准回答你的问题。

> 🎓 **适合场景**：实习作品展示 / 个人知识库 / RAG 学习参考

### 核心流程

```
用户上传文档          用户提出问题
     ↓                     ↓
  解析内容             语义检索
     ↓                     ↓
  文本切片      ←→    向量数据库
     ↓                     ↓
  生成向量           找到相关片段
                          ↓
                    LLM 结合上下文
                     生成精准回答
```

---

## 🏗️ 项目架构

```
rag/
├── src/
│   ├── main.py                  # FastAPI 入口（6 个 API + SSE 流式）
│   ├── config.py                # 统一配置（.env）
│   ├── models/schemas.py        # 7 个 Pydantic 数据模型
│   ├── document_loader/         # 文档加载（PDF/TXT/MD/DOCX）
│   ├── chunking/                # 递归文本切片策略
│   ├── embeddings/              # 本地/远程双模嵌入
│   ├── vector_store/            # ChromaDB 向量管理
│   ├── retrieval/               # 语义检索 + 重排序
│   ├── generation/              # LLM 生成（同步+流式）
│   └── pipeline/                # 完整流程编排
├── static/                      # 原生前端（HTML/CSS/JS）
├── tests/                       # 17 个单元 & 集成测试
├── demo_data/                   # 3 份不同格式示例文档
├── notebooks/demo.ipynb         # Jupyter 交互演示
├── .github/workflows/test.yml   # CI 自动测试
├── Dockerfile + docker-compose.yml
└── requirements.txt
```

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- 一个 LLM API Key（DeepSeek / OpenAI / 智谱AI / 通义千问 均可）

### 2. 安装 & 配置

```bash
# 克隆仓库
git clone https://github.com/你的用户名/rag-qa-system.git
cd rag-qa-system

# 安装依赖
pip install -r requirements.txt

# 配置 API Key（编辑 .env）
cp .env.example .env
# 然后编辑 .env，填入你的 API Key
```

### 3. 启动服务

```bash
python -m src.main
```

浏览器访问：

| 地址                          | 说明                |
| --------------------------- | ----------------- |
| http://localhost:8000       | 🎨 前端界面           |
| http://localhost:8000/docs  | 📖 Swagger API 文档 |
| http://localhost:8000/redoc | 📑 ReDoc 文档       |

### 4. Docker 部署

```bash
docker-compose up -d
```

> 📌 **无需配置 Embedding API**：默认使用本地模型 `MiniLM` 生成向量，上传文档完全免费。

---

## 📖 使用说明

### 上传文档

点击左侧「📄 上传文档」→ 选择文件。支持格式：

| 格式       | 扩展名     | 说明       |
| -------- | ------- | -------- |
| 纯文本      | `.txt`  | UTF-8 编码 |
| Markdown | `.md`   | 包含标题、代码块 |
| PDF      | `.pdf`  | 按页解析     |
| Word     | `.docx` | 提取段落文本   |

### 提问

在右侧输入框输入问题 → Enter 发送。系统会：

1. 从向量库中 **语义检索** 最相关的文档片段
2. 将片段作为上下文 **提交给 LLM**
3. 生成精准回答并 **附注引用来源**

### 流式输出

勾选右下角「流式输出」，回答会逐字显示，像 ChatGPT 一样。

---

## 🔌 API 接口

| 方法       | 路径                             | 说明             |
| -------- | ------------------------------ | -------------- |
| `GET`    | `/api/v1/health`               | 健康检查           |
| `POST`   | `/api/v1/documents/upload`     | 上传文档           |
| `GET`    | `/api/v1/documents`            | 文档列表           |
| `DELETE` | `/api/v1/documents/{filename}` | 删除文档           |
| `POST`   | `/api/v1/chat`                 | RAG 问答（同步）     |
| `POST`   | `/api/v1/chat/stream`          | RAG 问答（流式 SSE） |

---

## 🛠️ 技术栈

| 层级     | 技术                    | 为什么选它             |
| ------ | --------------------- | ----------------- |
| Web 框架 | **FastAPI**           | 高性能异步、自动生成 API 文档 |
| RAG 框架 | **LangChain**         | 业界标准，模块化程度高       |
| 向量数据库  | **ChromaDB**          | 轻量嵌入式，零外部依赖       |
| 嵌入模型   | **MiniLM**（本地）        | 免费、离线、无需 API Key  |
| LLM    | **DeepSeek / OpenAI** | 一行配置切换            |
| 前端     | **原生 HTML/CSS/JS**    | 零框架依赖，展示基础能力      |
| 测试     | **pytest**            | 17 个测试用例          |
| CI     | **GitHub Actions**    | 每次 push 自动跑测试     |
| 容器化    | **Docker**            | 一键部署              |

### 支持的 LLM 服务商

| 服务商      | API_BASE_URL                                        | 推荐模型            |
| -------- | --------------------------------------------------- | --------------- |
| OpenAI   | (留空)                                                | `gpt-4o-mini`   |
| DeepSeek | `https://api.deepseek.com/v1`                       | `deepseek-chat` |
| 智谱AI     | `https://open.bigmodel.cn/api/paas/v4/`             | `glm-4-flash`   |
| 通义千问     | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo`    |

---

## 🧪 测试

```bash
pytest tests/ -v
```

> 需要 API Key 的测试会自动跳过，不影响本地验证。

---

## 📋 项目亮点

- ✅ **模块化架构**：6 个核心模块，职责清晰，低耦合
- ✅ **本地 Embedding**：默认使用 MiniLM，免费离线无需 API
- ✅ **多格式支持**：PDF / Word / Markdown / TXT
- ✅ **流式输出**：SSE 实时逐字生成
- ✅ **来源追溯**：每个回答附带引用和相关度分数
- ✅ **自动测试**：GitHub Actions 持续集成
- ✅ **Docker 就绪**：一行命令部署
- ✅ **API 文档**：Swagger UI 交互式文档

---

## 📸 界面截图

运行后访问 http://localhost:8000，界面如下：

![](C:/Users/Alienware/AppData/Roaming/marktext/images/2026-07-19-16-03-47-image.png)

---

## 🔮 扩展方向

- [ ] **混合检索**：BM25 关键词 + 语义检索，提升准确率
- [ ] **重排序**：Cross-Encoder 对检索结果精排
- [ ] **多轮对话**：记住聊天历史，支持追问
- [ ] **权限管理**：用户认证 + 文档访问控制
- [ ] **图片支持**：多模态模型，图片也能问答
- [ ] **RAGAS 评估**：量化评估检索和生成质量
- [ ] **知识图谱**：结合 Neo4j 增强关系推理

---

## 📄 License

MIT © 2024
