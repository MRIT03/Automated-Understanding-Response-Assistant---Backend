from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.incident import Incident
from app.models.incident_type import IncidentType
from app.models.phone_call import PhoneCall
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
        stmt = (
            db.query(Incident)
            .options(joinedload(Incident.incident_type).joinedload(IncidentType.category))
            .filter(Incident.id == payload.incident_id)
        )
        incident = stmt.one_or_none()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")

        type_name = incident.incident_type.name if incident.incident_type else str(incident.incident_type_id)
        incident_context = (
            f"Incident #{incident.id} | type={type_name} | status={incident.status} "
            f"| priority={incident.priority} | address={incident.address or ''} "
            f"| caller={incident.caller_name or 'unknown'} | phone={incident.caller_phone or 'unknown'} "
            f"| description={incident.description or ''}"
        )

    if payload.call_id is not None:
        stmt = (
            db.query(PhoneCall)
            .options(joinedload(PhoneCall.employee))
            .filter(PhoneCall.id == payload.call_id)
        )
        phone_call = stmt.one_or_none()
        if not phone_call:
            raise HTTPException(status_code=404, detail="Phone call not found")

        employee_name = (
            f"{phone_call.employee.first_name} {phone_call.employee.last_name}"
            if phone_call.employee
            else str(phone_call.employee_id)
        )
        call_context = (
            f"Phone call #{phone_call.id} | employee={employee_name} "
            f"| caller_phone={phone_call.caller_phone or 'unknown'} "
            f"| started={phone_call.started_at} | notes={phone_call.notes or ''} "
            f"| transcript={phone_call.whisper_transcript or ''}"
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
