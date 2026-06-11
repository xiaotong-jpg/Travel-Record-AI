from __future__ import annotations

import json
import uuid
from collections.abc import Awaitable, Callable

import httpx
from fastapi import HTTPException

from app.core.config import settings


async def _request_with_retry(operation: Callable[[], Awaitable[httpx.Response]], retries: int = 2) -> httpx.Response:
    last_error: Exception | None = None
    for _ in range(retries + 1):
        try:
            response = await operation()
            if response.status_code in {429, 500, 502, 503, 504}:
                last_error = HTTPException(status_code=502, detail=f"vivo API 暂时不可用：{response.status_code}")
                continue
            return response
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            last_error = exc
    raise HTTPException(status_code=502, detail=f"vivo API 请求失败：{last_error}")


def extract_json_object(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end < start:
            raise HTTPException(status_code=502, detail="AI 返回内容不是 JSON")
        return json.loads(cleaned[start : end + 1])


async def chat_completion(messages: list[dict], *, max_tokens: int = 2048, temperature: float = 0.7) -> str:
    if not settings.vivo_app_key:
        raise HTTPException(status_code=500, detail="后端未配置 VIVO_APP_KEY")

    request_id = str(uuid.uuid4())
    url = f"{settings.vivo_api_base.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {settings.vivo_app_key}",
    }
    payload = {
        "model": settings.vivo_model,
        "messages": messages,
        "stream": False,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "thinking": {"type": "disabled"},
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await _request_with_retry(
            lambda: client.post(url, headers=headers, params={"request_id": request_id}, json=payload)
        )

    try:
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"vivo API 响应异常：{exc}") from exc

    if data.get("code") and data.get("code") != 0:
        raise HTTPException(status_code=502, detail=f"vivo API 返回错误：{data.get('message', data.get('code'))}")

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="vivo API 响应格式异常") from exc
