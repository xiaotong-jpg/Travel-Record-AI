from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


TravelStyle = Literal["手账风", "明信片风", "朋友圈风", "小红书风", "电影旁白风", "简洁记录风"]
PosterStyle = Literal["手账风", "小红书风", "清新风", "胶片风", "文艺风"]


class TravelGenerateRequest(BaseModel):
    place: str = Field(..., min_length=1, max_length=120)
    travel_date: date
    companion: Optional[str] = Field(default=None, max_length=120)
    mood: Optional[str] = Field(default=None, max_length=80)
    memory: str = Field(..., min_length=1)
    quote: Optional[str] = Field(default=None, max_length=255)
    style: TravelStyle


class TravelAIResult(BaseModel):
    title: str
    content: str
    location_desc: str = ""
    mood_tags: list[str] = Field(default_factory=list)
    stickers: list[str] = Field(default_factory=list)
    share_text: str = ""
    timeline_items: list[dict[str, Any]] = Field(default_factory=list)
    section_blocks: list[dict[str, Any]] = Field(default_factory=list)
    image_layout_suggestions: list[dict[str, Any]] = Field(default_factory=list)


class TravelRecordResponse(TravelAIResult):
    id: int
    place: str
    city: Optional[str] = None
    normalized_place: Optional[str] = None
    place_confidence: Optional[str] = None
    places: list[str] = Field(default_factory=list)
    place_regions: list[dict[str, str]] = Field(default_factory=list)
    travel_date: date
    companion: Optional[str] = None
    mood: Optional[str] = None
    memory: str
    quote: Optional[str] = None
    style: str
    source_type: str = "form"
    chat_session_id: Optional[str] = None
    image_urls: list[str] = Field(default_factory=list)
    hand_account_layout: Optional[dict[str, Any]] = None
    generated_image_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class YearSummaryResponse(BaseModel):
    summary: str


class TravelPosterGenerateRequest(BaseModel):
    style: PosterStyle = "手账风"


class TravelPosterGenerateResponse(BaseModel):
    image_url: str


class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    session_id: str
    reply: str
    travel_info: dict[str, Any] = Field(default_factory=dict)
    ready_to_generate: bool = False
    missing_fields: list[str] = Field(default_factory=list)


class RecommendRequest(BaseModel):
    city: Optional[str] = None
    current_place: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    preferences: list[str] = Field(default_factory=list)
    visited_places: list[str] = Field(default_factory=list)


class LocationResolveRequest(BaseModel):
    latitude: float
    longitude: float
    preferences: list[str] = Field(default_factory=list)
    visited_places: list[str] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    name: str
    reason: str
    estimated_time: str = ""
    tags: list[str] = Field(default_factory=list)
    route_tip: str = ""
    crowd_level: str = ""
    alternative: str = ""


class RecommendResponse(BaseModel):
    fallback: bool = False
    postcard_text: str = ""
    summary: str = ""
    recommendations: list[RecommendationItem] = Field(default_factory=list)


class LocationResolveResponse(RecommendResponse):
    city: str = ""
    current_place: str = ""
    description: str = ""
    confidence: str = "low"

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, value: Any) -> str:
        if isinstance(value, (int, float)):
            if value >= 0.8:
                return "high"
            if value >= 0.45:
                return "medium"
            return "low"
        return str(value or "low")
