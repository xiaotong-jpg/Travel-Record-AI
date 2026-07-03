from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.models.travel import TravelRecord
from app.schemas.travel import (
    TravelGenerateRequest,
    TravelPosterGenerateRequest,
    TravelPosterGenerateResponse,
    TravelPosterJobCreateResponse,
    TravelPosterJobStatusResponse,
    TravelRecordResponse,
    YearSummaryResponse,
)
from app.services.vivo_ai import call_vivo_travel, call_vivo_year_summary
from app.services.vivo_image import generate_travel_poster
from app.services.place_normalizer import normalize_place, normalize_place_local

router = APIRouter()

POSTER_JOBS: dict[str, dict[str, str | None]] = {}
MAX_POSTER_JOBS = 100


def _set_poster_job(job_id: str, **updates: str | None) -> None:
    job = POSTER_JOBS.setdefault(job_id, {"job_id": job_id, "status": "pending", "image_url": None, "error": None})
    job.update(updates)
    if len(POSTER_JOBS) > MAX_POSTER_JOBS:
        for old_id in list(POSTER_JOBS.keys())[: len(POSTER_JOBS) - MAX_POSTER_JOBS]:
            POSTER_JOBS.pop(old_id, None)


async def _run_poster_job(job_id: str, record_id: int, style: str) -> None:
    _set_poster_job(job_id, status="running", error=None)
    db = SessionLocal()
    try:
        record = db.get(TravelRecord, record_id)
        if not record:
            _set_poster_job(job_id, status="failed", error="旅行记录不存在")
            return
        image_url = await generate_travel_poster(to_response(record), style)
        record.exported_long_image_url = image_url
        record.style = style
        db.commit()
        _set_poster_job(job_id, status="succeeded", image_url=image_url, error=None)
    except HTTPException as exc:
        _set_poster_job(job_id, status="failed", error=str(exc.detail))
    except Exception as exc:
        _set_poster_job(job_id, status="failed", error=f"AI 图片日志生成失败：{exc}")
    finally:
        db.close()

def to_response(record: TravelRecord) -> TravelRecordResponse:
    normalized = normalize_place_local(record.place, record.content)
    data = {
        "id": record.id,
        "place": record.place,
        "city": record.city or normalized.city,
        "normalized_place": record.normalized_place or normalized.normalized_place,
        "place_confidence": record.place_confidence or normalized.confidence,
        "places": record.places or normalized.places or ([record.city] if record.city else []),
        "place_regions": record.place_regions or normalized.place_regions,
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
    place_info = await normalize_place(payload.place, f"{payload.memory}\n{ai_result.content}")
    record = TravelRecord(
        place=payload.place,
        city=place_info.city,
        normalized_place=place_info.normalized_place,
        place_confidence=place_info.confidence,
        places=place_info.places,
        place_regions=place_info.place_regions,
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


@router.get("/poster-jobs/{job_id}", response_model=TravelPosterJobStatusResponse)
def get_poster_job(job_id: str) -> TravelPosterJobStatusResponse:
    job = POSTER_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="AI 图片日志任务不存在或已过期")
    return TravelPosterJobStatusResponse(**job)


@router.post("/{record_id}/generate-poster-job", response_model=TravelPosterJobCreateResponse)
def create_poster_job(
    record_id: int,
    payload: TravelPosterGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> TravelPosterJobCreateResponse:
    record = db.get(TravelRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="旅行记录不存在")
    if not (record.image_urls or []):
        raise HTTPException(status_code=400, detail="请先上传至少一张旅行图片，再生成 AI 图片日志")
    job_id = uuid.uuid4().hex
    _set_poster_job(job_id, status="pending", image_url=None, error=None)
    background_tasks.add_task(_run_poster_job, job_id, record_id, payload.style)
    return TravelPosterJobCreateResponse(job_id=job_id, status="pending")

@router.get("/{record_id}", response_model=TravelRecordResponse)
def get_travel(record_id: int, db: Session = Depends(get_db)) -> TravelRecordResponse:
    record = db.get(TravelRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="旅行记录不存在")
    return to_response(record)



@router.delete("/{record_id}")
def delete_travel(record_id: int, db: Session = Depends(get_db)) -> dict[str, bool]:
    record = db.get(TravelRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="旅行记录不存在")
    db.delete(record)
    db.commit()
    return {"ok": True}


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
