from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.travel import Recommendation
from app.schemas.travel import (
    LocationResolveRequest,
    LocationResolveResponse,
    RecommendRequest,
    RecommendResponse,
    RecommendationItem,
)
from app.services.vivo_chat_client import chat_completion, extract_json_object
from app.services.vivo_geo_client import search_poi

router = APIRouter()


def _coordinate_label(latitude: float | None, longitude: float | None) -> str:
    if latitude is None or longitude is None:
        return "当前位置"
    return f"当前位置({latitude:.5f}, {longitude:.5f})"


def _fallback_items(place: str, preferences: list[str]) -> list[RecommendationItem]:
    primary = preferences[0] if preferences else "小众安静"
    secondary = preferences[1] if len(preferences) > 1 else "拍照打卡"
    return [
        RecommendationItem(
            name=f"{place}附近的慢行街区",
            reason=f"适合按{primary}的节奏走一段，停下来拍照、喝杯热饮，给下一页手账留一点生活感。",
            estimated_time="约 40-60 分钟",
            tags=["轻松", primary, "可步行"],
            route_tip="先沿主路慢走，再绕进人少的小巷、公园或水边支路。",
            crowd_level="中等",
            alternative="如果人多，可以选择附近公园、书店或安静咖啡馆作为替代。",
        ),
        RecommendationItem(
            name=f"{place}附近的文化停靠点",
            reason=f"给旅程加一点故事感，也更符合{secondary}的偏好，适合作为下一篇旅行日志的标题。",
            estimated_time="约 1-2 小时",
            tags=["文化", "手账感", secondary],
            route_tip="建议下午或傍晚前往，光线更柔和，也更适合拍摄外观和街景。",
            crowd_level="较少",
            alternative="可改为附近展馆、老街、寺庙建筑外观或城市公共空间。",
        ),
    ]


def _fallback_recommend(payload: RecommendRequest, poi_data: dict | None = None) -> RecommendResponse:
    place = payload.current_place or payload.city or _coordinate_label(payload.latitude, payload.longitude)
    items = _fallback_items(place, payload.preferences)
    return RecommendResponse(
        fallback=True,
        postcard_text=f"从{place}再往前走一点，也许下一页回忆就在转角。",
        summary="已根据当前位置、坐标和偏好生成本地兜底推荐。配置大模型 API key 后，会进一步解析城市、街区和附近景点。",
        recommendations=items,
    )


def _fallback_location(payload: LocationResolveRequest, reason: str | None = None) -> LocationResolveResponse:
    place = _coordinate_label(payload.latitude, payload.longitude)
    items = _fallback_items(place, payload.preferences)
    if settings.vivo_app_key:
        description = reason or "已记录浏览器返回的经纬度；AI 位置解析暂时失败，先使用坐标生成附近推荐。"
        summary = "已根据坐标和偏好生成兜底推荐。你也可以手动补充城市或地点，让推荐更精确。"
    else:
        description = "已记录浏览器返回的经纬度；当前未配置大模型 API key，无法进一步反查城市和地标。"
        summary = "你可以手动补充城市或地点；配置大模型 API key 后，系统会自动分析坐标并填入更具体的位置。"
    return LocationResolveResponse(
        fallback=True,
        city="当前位置",
        current_place=place,
        description=description,
        confidence="low",
        postcard_text=f"从{place}出发，先把附近适合慢走的地方整理成下一站。",
        summary=summary,
        recommendations=items,
    )


async def _resolve_location_with_ai(payload: LocationResolveRequest) -> LocationResolveResponse:
    if not settings.vivo_app_key:
        return _fallback_location(payload)

    prompt = f"""请根据用户浏览器定位得到的经纬度，尽可能判断用户所在城市、区县/街区或附近地标，并生成附近景点推荐。
如果无法精确反查，请给出低置信度结果，但不要编造门牌级精确位置。

必须只返回 JSON，结构如下：
{{
  "fallback": false,
  "city": "",
  "current_place": "",
  "description": "",
  "confidence": "high|medium|low",
  "postcard_text": "",
  "summary": "",
  "recommendations": [
    {{"name": "", "reason": "", "estimated_time": "", "tags": [], "route_tip": "", "crowd_level": "", "alternative": ""}}
  ]
}}

输入：
{json.dumps(payload.model_dump(), ensure_ascii=False)}
"""
    try:
        content = await chat_completion(
            [
                {"role": "system", "content": "你是旅行位置分析和附近景点推荐助手，回答必须准确、克制、可执行。"},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1800,
            temperature=0.4,
        )
        data = extract_json_object(content)
        return LocationResolveResponse(**data)
    except Exception as exc:
        return _fallback_location(payload, f"已记录浏览器返回的经纬度；AI 位置解析暂时失败：{exc}")


async def _ai_recommend(payload: RecommendRequest, poi_data: dict, fallback: bool) -> RecommendResponse:
    if not settings.vivo_app_key:
        return _fallback_recommend(payload, poi_data)

    prompt = f"""请根据当前位置、经纬度、附近 POI、用户偏好和已去过地点，推荐下一站旅行路线。
如果 city/current_place 为空，请优先根据 latitude/longitude 分析用户所在地，再给附近景点推荐。
必须只返回 JSON：
{{
  "fallback": false,
  "postcard_text": "",
  "summary": "",
  "recommendations": [
    {{"name": "", "reason": "", "estimated_time": "", "tags": [], "route_tip": "", "crowd_level": "", "alternative": ""}}
  ]
}}

输入：
{json.dumps({"request": payload.model_dump(), "poi": poi_data, "geo_fallback": fallback}, ensure_ascii=False)}
"""
    try:
        content = await chat_completion(
            [
                {"role": "system", "content": "你是温柔但务实的 AI 旅行推荐搭子，输出低营销感、可执行、有叙事感的推荐。"},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1600,
            temperature=0.7,
        )
        data = extract_json_object(content)
        return RecommendResponse(**data)
    except Exception:
        return _fallback_recommend(payload, poi_data)


@router.post("/resolve-location", response_model=LocationResolveResponse)
async def resolve_location(payload: LocationResolveRequest) -> LocationResolveResponse:
    return await _resolve_location_with_ai(payload)


@router.post("/nearby", response_model=RecommendResponse)
async def recommend_nearby(payload: RecommendRequest, db: Session = Depends(get_db)) -> RecommendResponse:
    resolved: LocationResolveResponse | None = None
    if (not payload.city or not payload.current_place) and payload.latitude is not None and payload.longitude is not None:
        resolved = await _resolve_location_with_ai(
            LocationResolveRequest(
                latitude=payload.latitude,
                longitude=payload.longitude,
                preferences=payload.preferences,
                visited_places=payload.visited_places,
            )
        )
        payload = payload.model_copy(
            update={
                "city": payload.city or resolved.city,
                "current_place": payload.current_place or resolved.current_place,
            }
        )

    poi_data, geo_fallback = await search_poi(payload.city, payload.current_place)
    result = resolved if resolved and resolved.recommendations else await _ai_recommend(payload, poi_data, geo_fallback)
    record = Recommendation(
        city=payload.city,
        current_place=payload.current_place,
        latitude=payload.latitude,
        longitude=payload.longitude,
        preferences_json=payload.preferences,
        visited_places_json=payload.visited_places,
        poi_json=poi_data,
        result_json=result.model_dump(),
    )
    db.add(record)
    db.commit()
    return RecommendResponse(
        fallback=result.fallback,
        postcard_text=result.postcard_text,
        summary=result.summary,
        recommendations=result.recommendations,
    )
