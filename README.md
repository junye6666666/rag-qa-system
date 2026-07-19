# 📚 RAG 知识库问答系统

> 基于 **检索增强生成（Retrieval-Augmented Generation）** 的智能知识库问答系统
>
> 上传你的文档 → 系统自动理解内容 → 精准回答你的问题

---

## 🎯 项目简介

这是一个从零构建的、生产级 RAG 系统，适合用于：
- **实习作品展示**：展示全栈开发能力、AI 应用理解、软件工程实践
- **个人知识库**：为你的学习资料建立可问答的知识库
- **学习 RAG 原理**：代码结构清晰，注释完善，便于学习

### 核心流程

```
用户上传文档 → 解析内容 → 文本切片 → 生成向量 → 存入向量数据库
                                                          ↓
用户提出问题 → 语义检索 → 找到相关片段 → LLM 结合上下文生成回答
```

---

## 🏗️ 项目架构

```
rag/
├── src/
│   ├── main.py                  # FastAPI 应用入口
│   ├── config.py                # 配置管理（.env）
│   ├── models/schemas.py        # Pydantic 数据模型
│   ├── document_loader/         # 文档加载（支持 PDF/TXT/MD/DOCX）
│   ├── chunking/                # 文本切片策略
│   ├── embeddings/              # 向量嵌入生成
│   ├── vector_store/            # ChromaDB 向量存储
│   ├── retrieval/               # 语义检索模块
│   ├── generation/              # LLM 生成模块
│   └── pipeline/                # 完整 RAG 流程编排
├── static/                      # 前端（原生 HTML/CSS/JS）
├── tests/                       # 单元测试 & 集成测试
├── demo_data/                   # 示例知识库文档
├── data/                        # 上传文档存储
├── Dockerfile                   # Docker 镜像
├── docker-compose.yml           # 一键部署
└── requirements.txt             # Python 依赖
```

---

## 🚀 快速开始

### 1. 环境准备

- Python 3.10+
- 一个 LLM API Key（支持 OpenAI / 智谱AI / 通义千问 / DeepSeek 等）

### 2. 安装依赖

```bash
# 克隆或进入项目目录
cd rag

# 创建虚拟环境（推荐）
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# 以智谱AI 为例：
#   API_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
#   API_KEY=你的API密钥
#   MODEL_NAME=glm-4-flash
#   EMBEDDING_MODEL=embedding-2
```

### 4. 启动服务

```bash
python -m src.main
```

访问：
- 🌐 **前端界面**：http://localhost:8000
- 📖 **API 文档**：http://localhost:8000/docs
- 📑 **ReDoc 文档**：http://localhost:8000/redoc

### 5. Docker 部署（可选）

```bash
docker-compose up -d
```

---

## 📖 使用说明

### 上传文档

1. 点击左侧「📄 上传文档」按钮
2. 选择文档（支持 PDF、TXT、Markdown、Word）
3. 系统自动解析、切片、生成向量并存入知识库

### 提问

1. 在右侧输入框输入问题
2. 按 Enter 发送（Shift + Enter 换行）
3. 系统检索相关文档片段 → LLM 生成回答 → 展示引用来源

### 管理文档

- 左侧面板显示所有已导入的文档
- 点击文档右侧的 ✕ 可删除文档

---

## 🔌 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/health` | 健康检查 |
| `POST` | `/api/v1/documents/upload` | 上传文档 |
| `GET` | `/api/v1/documents` | 文档列表 |
| `DELETE` | `/api/v1/documents/{filename}` | 删除文档 |
| `POST` | `/api/v1/chat` | RAG 问答（同步） |
| `POST` | `/api/v1/chat/stream` | RAG 问答（流式 SSE） |

---

## 🧪 运行测试

```bash
pytest tests/ -v
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **Web 框架** | FastAPI | 高性能异步框架，自动生成 API 文档 |
| **RAG 框架** | LangChain | 业界标准 RAG 框架 |
| **向量数据库** | ChromaDB | 轻量级嵌入式向量存储 |
| **LLM API** | OpenAI 兼容 | 支持 OpenAI / 智谱 / 通义千问 / DeepSeek |
| **前端** | 原生 HTML/CSS/JS | 零依赖，展示前端基础能力 |
| **容器化** | Docker | 一键部署 |
| **测试** | pytest | 单元测试和集成测试 |

### 支持的 API 服务商

| 服务商 | API_BASE_URL | 推荐模型 |
|--------|-------------|---------|
| OpenAI | (留空) | gpt-4o-mini |
| 智谱AI | `https://open.bigmodel.cn/api/paas/v4/` | glm-4-flash |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | qwen-turbo |
| DeepSeek | `https://api.deepseek.com/v1` | deepseek-chat |
| 任何兼容服务 | 填入对应地址 | 对应模型名 |

---

## 📝 项目亮点

1. **模块化架构**：每个模块职责清晰，低耦合，易扩展
2. **多格式支持**：PDF、Word、Markdown、TXT 一站式处理
3. **流式输出**：支持 SSE 实时流式回答，提升用户体验
4. **来源追溯**：每个回答都附注引用来源和相关性分数
5. **OpenAI 兼容**：一行配置即可切换不同 LLM 服务商
6. **完整文档**：中英文 README、API 文档、Demo Notebook
7. **容器化部署**：Docker 一键启动
8. **测试覆盖**：核心模块均有单元测试

---

## 🔮 扩展建议

以下是可以进一步优化的方向，适合作为后续学习或面试亮点：

- [ ] 混合检索（Hybrid Search）：结合 BM25 关键词检索 + 语义检索
- [ ] 重排序（Reranker）：使用 Cross-Encoder 对检索结果重排序
- [ ] 多轮对话：支持带历史上下文的连续问答
- [ ] 权限管理：用户认证和文档权限控制
- [ ] 更大规模：迁移到 Milvus / Weaviate 等分布式向量数据库
- [ ] 图片支持：使用多模态模型支持图片问答
- [ ] 评估体系：RAGAS 评估检索和生成质量

---

## 📄 License

MIT License — 自由使用和修改
