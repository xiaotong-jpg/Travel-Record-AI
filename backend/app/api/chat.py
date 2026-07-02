from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.travel import ChatSession, TravelRecord
from app.schemas.travel import ChatMessageRequest, ChatMessageResponse, TravelGenerateRequest, TravelRecordResponse
from app.services.travel_memory import missing_fields
from app.services.vivo_ai import call_vivo_travel, today_as_date
from app.services.vivo_chat_agent import chat_as_travel_agent
from app.services.place_normalizer import normalize_place
from app.api.travel import to_response

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _get_or_create_session(db: Session, session_id: str | None) -> ChatSession:
    if session_id:
        session = db.scalar(select(ChatSession).where(ChatSession.session_id == session_id))
        if session:
            return session
    session = ChatSession(session_id=str(uuid.uuid4()), messages_json=[], travel_info_json={}, uploaded_images_json=[])
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(payload: ChatMessageRequest, db: Session = Depends(get_db)) -> ChatMessageResponse:
    session = _get_or_create_session(db, payload.session_id)
    messages = list(session.messages_json or [])
    messages.append({"role": "user", "content": payload.message})

    reply, travel_info = await chat_as_travel_agent(payload.message, messages, session.travel_info_json or {})
    missing = missing_fields(travel_info)
    ready = not missing
    messages.append({"role": "assistant", "content": reply})

    session.messages_json = messages
    session.travel_info_json = travel_info
    session.finished = ready
    db.commit()
    return ChatMessageResponse(
        session_id=session.session_id,
        reply=reply,
        travel_info=travel_info,
        ready_to_generate=ready,
        missing_fields=missing,
    )


async def _save_images(files: list[UploadFile]) -> list[str]:
    urls: list[str] = []
    for file in files[:9]:
        suffix = Path(file.filename or "").suffix.lower() or ".jpg"
        if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise HTTPException(status_code=400, detail="仅支持 jpg、png、webp 图片")
        name = f"{uuid.uuid4().hex}{suffix}"
        path = UPLOAD_DIR / name
        path.write_bytes(await file.read())
        urls.append(f"/uploads/{name}")
    return urls


@router.post("/generate-travel-log", response_model=TravelRecordResponse)
async def generate_travel_log(
    session_id: str = Form(...),
    travel_info_json: str = Form("{}"),
    images: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
) -> TravelRecordResponse:
    session = db.scalar(select(ChatSession).where(ChatSession.session_id == session_id))
    if not session:
        raise HTTPException(status_code=404, detail="聊天会话不存在")

    frontend_info = json.loads(travel_info_json or "{}")
    travel_info = {**(session.travel_info_json or {}), **frontend_info}
    image_urls = await _save_images(images)
    session.uploaded_images_json = list(session.uploaded_images_json or []) + image_urls

    payload = TravelGenerateRequest(
        place=travel_info.get("place") or "未命名旅行地",
        travel_date=today_as_date(travel_info.get("travel_date")),
        companion=travel_info.get("companion") or None,
        mood=travel_info.get("mood") or None,
        memory=travel_info.get("memory") or "这是一段还没来得及说完的旅行记忆。",
        quote=travel_info.get("quote") or None,
        style=travel_info.get("style") or "手账风",
    )
    try:
        ai_result, raw_response = await call_vivo_travel(payload, image_urls)
        place_info = await normalize_place(payload.place, f"{payload.memory}\n{ai_result.content}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"旅行手账生成失败：{exc}") from exc
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
        source_type="chat",
        chat_session_id=session.session_id,
        image_urls=image_urls,
        hand_account_layout={
            "timeline_items": ai_result.timeline_items,
            "section_blocks": ai_result.section_blocks,
            "image_layout_suggestions": ai_result.image_layout_suggestions,
        },
        raw_ai_response=raw_response,
    )
    session.finished = True
    db.add(record)
    db.commit()
    db.refresh(record)
    return to_response(record)
