from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, BigInteger, Date, DateTime, Float, Integer, JSON, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT, MEDIUMTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


id_type = BigInteger().with_variant(BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")
long_text_type = Text().with_variant(MEDIUMTEXT, "mysql")


class TravelRecord(Base):
    __tablename__ = "travel_records"

    id: Mapped[int] = mapped_column(id_type, primary_key=True, autoincrement=True)
    place: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    normalized_place: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    place_confidence: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    places: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    place_regions: Mapped[Optional[list[dict]]] = mapped_column(JSON, nullable=True)
    travel_date: Mapped[date] = mapped_column(Date, nullable=False)
    companion: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    mood: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    memory: Mapped[str] = mapped_column(Text, nullable=False)
    quote: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    style: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    content: Mapped[str] = mapped_column(long_text_type, nullable=False)
    location_desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mood_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    stickers: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    share_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, default="form")
    chat_session_id: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    image_urls: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    hand_account_layout: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    exported_long_image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    raw_ai_response: Mapped[Optional[str]] = mapped_column(long_text_type, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(id_type, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    messages_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    travel_info_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    uploaded_images_json: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    finished: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(id_type, primary_key=True, autoincrement=True)
    city: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    current_place: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    preferences_json: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    visited_places_json: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    poi_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
