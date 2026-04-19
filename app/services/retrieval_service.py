from __future__ import annotations

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings


class RetrievalService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        self.embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )
        self.vector_store = Chroma(
            collection_name=settings.chroma_collection_name,
            persist_directory=settings.chroma_persist_directory,
            embedding_function=self.embeddings,
        )

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None) -> None:
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)

    def similarity_search(self, query: str, k: int = 4) -> list[str]:
        docs = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
