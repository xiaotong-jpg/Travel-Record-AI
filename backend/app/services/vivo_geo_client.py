from __future__ import annotations

import uuid

import httpx

from app.core.config import settings


async def search_poi(city: str | None, keywords: str | None) -> tuple[dict, bool]:
    if not settings.vivo_app_key or not city or not keywords:
        return {"pois": [], "total": 0}, True

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.vivo_app_key}",
    }
    params = {
        "keywords": keywords,
        "city": city,
        "page_num": 1,
        "page_size": 10,
        "requestId": str(uuid.uuid4()),
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get("https://api-ai.vivo.com.cn/search/geo", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        pois = data.get("pois") or []
        return {"pois": pois, "total": data.get("total") or data.get("totalCount") or len(pois)}, False
    except Exception:
        return {"pois": [], "total": 0}, True
