from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.call import Call
from app.models.incident import Incident
from app.schemas.assistant import (
    AssistantQueryRequest,
    AssistantQueryResponse,
    KnowledgeIngestRequest,
)
from app.schemas.common import Message
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post("/knowledge", response_model=Message, status_code=status.HTTP_201_CREATED)
def ingest_knowledge(payload: KnowledgeIngestRequest) -> Message:
    try:
        retrieval = RetrievalService()
        retrieval.add_texts(payload.texts, payload.metadatas)
        return Message(message="Knowledge ingested successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Knowledge ingestion failed: {exc}") from exc


@router.post("/query", response_model=AssistantQueryResponse)
def query_assistant(payload: AssistantQueryRequest, db: Session = Depends(get_db)) -> AssistantQueryResponse:
    incident_context = "No incident selected."
    call_context = "No call selected."

    if payload.incident_id is not None:
        incident = (
            db.query(Incident)
            .options(joinedload(Incident.incident_type))
            .filter(Incident.id == payload.incident_id)
            .one_or_none()
        )
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        incident_context = (
            f"Incident #{incident.incident_number} | type={incident.incident_type.name if incident.incident_type else incident.incident_type_id} "
            f"| status={incident.status.value} | priority={incident.priority.value} | address={incident.location_address} "
            f"| details={incident.location_details or ''} | description={incident.description or ''} "
            f"| units_requested={incident.units_requested} | units_dispatched={incident.units_dispatched}"
        )

    if payload.call_id is not None:
        call = (
            db.query(Call)
            .options(joinedload(Call.dispatcher), joinedload(Call.incident))
            .filter(Call.id == payload.call_id)
            .one_or_none()
        )
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        call_context = (
            f"Call #{call.call_reference} | dispatcher={call.dispatcher.full_name if call.dispatcher else call.dispatcher_id} "
            f"| status={call.call_status.value} | priority={call.priority.value} | location={call.reported_location} "
            f"| caller={call.caller_name or 'unknown'} | phone={call.caller_phone or 'unknown'} "
            f"| summary={call.summary or ''} | notes={call.dispatcher_notes or ''} | transcript={call.transcript or ''}"
        )

    retrieved_context: list[str] = []
    if payload.include_retrieval:
        try:
            retrieval = RetrievalService()
            retrieved_context = retrieval.similarity_search(payload.question, k=payload.max_documents)
        except ValueError:
            retrieved_context = []

    structured_context = f"{incident_context}\n{call_context}"

    try:
        llm = LLMService()
        answer = llm.answer_question(payload.question, structured_context, retrieved_context)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Assistant request failed: {exc}") from exc

    return AssistantQueryResponse(answer=answer, retrieved_context=retrieved_context)
