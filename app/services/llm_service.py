from __future__ import annotations

from langchain_openai import ChatOpenAI

from app.core.config import settings


SYSTEM_PROMPT = """
You are an emergency dispatch operations assistant for a fire/EMS/rescue control room.
Give concise, practical, safety-aware operational support.
Do not invent facts that are not present in the incident, call, or retrieved documents.
If information is missing, clearly say what is missing.
""".strip()


class LLMService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        self.client = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.2,
        )

    def answer_question(self, question: str, structured_context: str, retrieved_context: list[str] | None = None) -> str:
        knowledge_block = "\n\n".join(retrieved_context or [])
        prompt = f"""
{SYSTEM_PROMPT}

Structured incident and call context:
{structured_context}

Retrieved reference context:
{knowledge_block if knowledge_block else 'No retrieval context provided.'}

Dispatcher question:
{question}
""".strip()
        response = self.client.invoke(prompt)
        return getattr(response, "content", str(response))
