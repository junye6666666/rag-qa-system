"""LLM 生成器 — 调用大语言模型生成回答"""

from typing import Optional, AsyncIterator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from ..config import settings


# ============================================================
# Prompt 模板
# ============================================================

SYSTEM_PROMPT = """你是一个知识库问答助手。你的任务是根据提供的文档内容回答用户的问题。

请严格遵循以下规则：
1. **仅根据提供的文档内容回答**。如果文档中没有相关信息，请明确告知用户。
2. 回答时**引用具体的文档来源**（如"根据 [文档名]..."）。
3. 保持回答简洁、准确、有条理。
4. 如果文档内容不足以回答，请说"根据当前知识库中的文档，我无法回答这个问题"。
5. 使用与用户相同的语言回答（中文问则中文答，英文问则英文答）。
6. 不要编造文档中没有的信息。"""


class LLMGenerator:
    """
    LLM 生成器。

    使用 OpenAI 兼容的 Chat Completion API。
    支持同步生成和流式输出。
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.3,
    ):
        kwargs = {
            "model": model or settings.model_name,
            "api_key": api_key or settings.api_key,
            "temperature": temperature,
        }
        if base_url or settings.api_base_url:
            kwargs["base_url"] = base_url or settings.api_base_url

        self._llm = ChatOpenAI(**kwargs)
        self._model = kwargs["model"]
        self._streaming_llm = ChatOpenAI(**kwargs, streaming=True)

    @property
    def model(self) -> str:
        return self._model

    def generate(self, question: str, context: str) -> str:
        """
        基于上下文生成回答（同步）。

        Args:
            question: 用户问题
            context: 检索到的文档上下文

        Returns:
            生成的回答文本
        """
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=f"## 参考文档内容\n\n{context}\n\n---\n\n## 用户问题\n\n{question}"
            ),
        ]

        response = self._llm.invoke(messages)
        return response.content

    async def generate_stream(
        self, question: str, context: str
    ) -> AsyncIterator[str]:
        """
        基于上下文生成回答（流式）。

        Args:
            question: 用户问题
            context: 检索到的文档上下文

        Yields:
            增量生成的文本片段
        """
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=f"## 参考文档内容\n\n{context}\n\n---\n\n## 用户问题\n\n{question}"
            ),
        ]

        async for chunk in self._streaming_llm.astream(messages):
            if chunk.content:
                yield chunk.content
