from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class AssistantQueryRequest(BaseModel):
    question: str = Field(min_length=5)
    incident_id: int | None = None
    call_id: int | None = None
    include_retrieval: bool = True
    max_documents: int = Field(default=4, ge=1, le=10)


class AssistantQueryResponse(BaseModel):
    answer: str
    retrieved_context: List[str] = []


class KnowledgeIngestRequest(BaseModel):
    texts: List[str] = Field(min_length=1)
    metadatas: List[dict] | None = None
