from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.travel import TravelRecord
from app.schemas.travel import (
    TravelGenerateRequest,
    TravelPosterGenerateRequest,
    TravelPosterGenerateResponse,
    TravelRecordResponse,
    YearSummaryResponse,
)
from app.services.vivo_ai import call_vivo_travel, call_vivo_year_summary
from app.services.vivo_image import generate_travel_poster

router = APIRouter()


def to_response(record: TravelRecord) -> TravelRecordResponse:
    data = {
        "id": record.id,
        "place": record.place,
        "travel_date": record.travel_date,
        "companion": record.companion,
        "mood": record.mood,
        "memory": record.memory,
        "quote": record.quote,
        "style": record.style,
        "title": record.title,
        "content": record.content,
        "location_desc": record.location_desc or "",
        "mood_tags": record.mood_tags or [],
        "stickers": record.stickers or [],
        "share_text": record.share_text or "",
        "timeline_items": (record.hand_account_layout or {}).get("timeline_items", []),
        "section_blocks": (record.hand_account_layout or {}).get("section_blocks", []),
        "image_layout_suggestions": (record.hand_account_layout or {}).get("image_layout_suggestions", []),
        "source_type": record.source_type or "form",
        "chat_session_id": record.chat_session_id,
        "image_urls": record.image_urls or [],
        "hand_account_layout": record.hand_account_layout,
        "generated_image_url": record.exported_long_image_url,
        "created_at": record.created_at,
    }
    return TravelRecordResponse(**data)


@router.post("/generate", response_model=TravelRecordResponse)
async def generate_travel(payload: TravelGenerateRequest, db: Session = Depends(get_db)) -> TravelRecordResponse:
    ai_result, raw_response = await call_vivo_travel(payload)
    record = TravelRecord(
        place=payload.place,
        travel_date=payload.travel_date,
        companion=payload.companion,
        mood=payload.mood,
        memory=payload.memory,
        quote=payload.quote,
        style=payload.style,
        title=ai_result.title,
        content=ai_result.content,
        location_desc=ai_result.location_desc,
        mood_tags=ai_result.mood_tags,
        stickers=ai_result.stickers,
        share_text=ai_result.share_text,
        hand_account_layout={
            "timeline_items": ai_result.timeline_items,
            "section_blocks": ai_result.section_blocks,
            "image_layout_suggestions": ai_result.image_layout_suggestions,
        },
        raw_ai_response=raw_response,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return to_response(record)


@router.get("/list", response_model=list[TravelRecordResponse])
def list_travel(db: Session = Depends(get_db)) -> list[TravelRecordResponse]:
    records = db.scalars(select(TravelRecord).order_by(TravelRecord.created_at.desc())).all()
    return [to_response(record) for record in records]


@router.get("/{record_id}", response_model=TravelRecordResponse)
def get_travel(record_id: int, db: Session = Depends(get_db)) -> TravelRecordResponse:
    record = db.get(TravelRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="旅行记录不存在")
    return to_response(record)


@router.post("/{record_id}/generate-poster", response_model=TravelPosterGenerateResponse)
async def generate_poster(
    record_id: int,
    payload: TravelPosterGenerateRequest,
    db: Session = Depends(get_db),
) -> TravelPosterGenerateResponse:
    record = db.get(TravelRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="旅行记录不存在")
    image_url = await generate_travel_poster(to_response(record), payload.style)
    record.exported_long_image_url = image_url
    record.style = payload.style
    db.commit()
    return TravelPosterGenerateResponse(image_url=image_url)


@router.post("/year-summary", response_model=YearSummaryResponse)
async def year_summary(db: Session = Depends(get_db)) -> YearSummaryResponse:
    records = db.scalars(select(TravelRecord).order_by(TravelRecord.travel_date.desc(), TravelRecord.created_at.desc())).all()
    payload = [
        {
            "place": record.place,
            "travel_date": record.travel_date.isoformat(),
            "title": record.title,
            "mood_tags": record.mood_tags or [],
            "summary": record.content[:160],
        }
        for record in records
    ]
    summary = await call_vivo_year_summary(payload)
    return YearSummaryResponse(summary=summary)
