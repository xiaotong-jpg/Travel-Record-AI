from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.travel import Recommendation
from app.schemas.travel import RecommendRequest, RecommendResponse, RecommendationItem
from app.services.vivo_chat_client import chat_completion, extract_json_object
from app.services.vivo_geo_client import search_poi

router = APIRouter()


def _fallback_recommend(payload: RecommendRequest, poi_data: dict) -> RecommendResponse:
    place = payload.current_place or payload.city or "当前位置"
    preferences = payload.preferences or ["小众安静", "拍照打卡"]
    items = [
        RecommendationItem(
            name=f"{place}附近的慢行街区",
            reason=f"适合按{preferences[0]}的节奏走一段，停下来拍照或喝杯热饮。",
            estimated_time="约 40-60 分钟",
            tags=["轻松", preferences[0], "可步行"],
            route_tip="先沿主路慢走，再绕进人少的小巷或湖边支路。",
            crowd_level="中等",
            alternative="如果人多，可以选择临近的公园或书店作为替代。",
        ),
        RecommendationItem(
            name=f"{payload.city or place}的一处文化停靠点",
            reason="给旅程加一点故事感，适合作为下一页手账的小标题。",
            estimated_time="约 1-2 小时",
            tags=["文化", "手账感", "安静"],
            route_tip="建议下午或傍晚前往，光线更柔和。",
            crowd_level="较少",
            alternative="可改为附近展馆、老街或寺庙建筑外观路线。",
        ),
    ]
    return RecommendResponse(
        fallback=True,
        postcard_text=f"从{place}再往前走一点，也许下一页回忆就在转角。",
        summary="我先按当前位置和偏好给出温柔版路线。定位或 POI 不稳定时，推荐会偏向通用但可执行的旅行建议。",
        recommendations=items,
    )


async def _ai_recommend(payload: RecommendRequest, poi_data: dict, fallback: bool) -> RecommendResponse:
    if not settings.vivo_app_key:
        return _fallback_recommend(payload, poi_data)

    prompt = f"""请根据当前位置、附近 POI、当前时间、用户偏好和已去过地点，推荐下一步旅行路线。
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
                {"role": "system", "content": "你是温柔的 AI 旅行推荐搭子，输出低营销感、可执行、有旅行叙事感的推荐。"},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1600,
            temperature=0.7,
        )
        data = extract_json_object(content)
        return RecommendResponse(**data)
    except Exception:
        return _fallback_recommend(payload, poi_data)


@router.post("/nearby", response_model=RecommendResponse)
async def recommend_nearby(payload: RecommendRequest, db: Session = Depends(get_db)) -> RecommendResponse:
    poi_data, geo_fallback = await search_poi(payload.city, payload.current_place)
    result = await _ai_recommend(payload, poi_data, geo_fallback)
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
    return result
