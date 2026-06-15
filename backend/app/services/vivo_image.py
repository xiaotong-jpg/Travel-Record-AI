from __future__ import annotations

import base64
import mimetypes
import time
import uuid
from pathlib import Path
from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.travel import TravelRecordResponse


GENERATED_DIR = Path(__file__).resolve().parents[2] / "uploads" / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads"


STYLE_PROMPTS = {
    "手账风": """
手账风，贴近参考图：米白纸张纹理、深青蓝中文标题、拍立得照片拼贴、纸胶带、旅行邮戳、手写标注、植物叶片、水彩地标。
重点是“旅行日志手账页面”，整体温柔、精致、像真实手工拼贴。
""",
    "小红书风": """
小红书风，生活方式分享海报：更明亮的暖白底、清爽网格排版、贴纸标签、时髦标题、精致阴影、适合社交媒体发布。
重点是“精致攻略分享感”，照片更整齐，文案像种草笔记。
""",
    "清新风": """
清新风，浅蓝、鼠尾草绿和留白：水彩晕染、植物线稿、空气感、轻盈透明贴纸、干净排版。
重点是“清爽治愈旅行日记”，减少厚重胶片和强烈复古色。
""",
    "胶片风": """
胶片风，复古旅行相册：暖色颗粒、胶片边框、日期戳、暗角、相纸质感、照片墙布局、手写地点备注。
重点是“复古胶片回忆”，色调偏暖，画面像冲印照片拼贴。
""",
    "文艺风": """
文艺风，诗意杂志内页：克制高级的留白、宋体标题、淡墨水彩、手绘地标、细线装饰、短诗式文案。
重点是“安静、文学、艺术展览海报感”，不要过多贴纸。
""",
}


def _api_root() -> str:
    return settings.vivo_api_base.rstrip("/").removesuffix("/v1")


def _record_prompt(record: TravelRecordResponse, style: str) -> str:
    tags = "、".join((record.mood_tags or [])[:4] + (record.stickers or [])[:3])
    image_count = len(record.image_urls or [])
    style_prompt = STYLE_PROMPTS.get(style, STYLE_PROMPTS["手账风"])
    return f"""
生成一张精美的中文旅行日志图片，这是一张“最终可保存分享的图片”，不是网页截图，不要出现按钮、导航栏、输入框。

风格：{style_prompt}

画面要求：
1. 竖版移动端海报构图，米白色纸张纹理背景，圆角手机页面质感。
2. 顶部大标题使用中文“旅行日志”，深青蓝色，优雅宋体或手账字体。
3. 展示日期：{record.travel_date}，地点主标题：{record.place}。
4. 加入定位图标、旅行邮戳、浅色地标水彩、植物叶片、手绘小爱心、纸胶带。
5. 中部做拍立得照片拼贴区域，像示例图一样有 2 张倾斜照片和手写中文 caption。
6. 下方可有圆形美食/风景照片贴纸、便签纸、箭头涂鸦。
7. 日志文案参考：{record.memory[:120]}。
8. 心情与标签：{tags or record.mood or "温柔、松弛、旅行记忆"}。
9. 如果用户上传了 {image_count} 张图片，请在画面中体现照片拼贴布局；不要生成真实人脸特写。
10. 文字必须清晰可读，排版高级，避免杂乱，不要二维码，不要水印，不要应用按钮。
11. 必须严格体现所选风格“{style}”，不同风格之间视觉差异要明显，不要输出通用模板。
""".strip()


async def _download_image(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.get(url)
    response.raise_for_status()
    return response.content


def _local_upload_to_data_url(image_url: str) -> str | None:
    if not image_url.startswith("/uploads/"):
        return None

    relative = image_url.removeprefix("/uploads/").replace("/", "\\")
    path = (UPLOAD_ROOT / relative).resolve()
    try:
        path.relative_to(UPLOAD_ROOT.resolve())
    except ValueError:
        return None
    if not path.exists() or not path.is_file():
        return None

    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _image_inputs(record: TravelRecordResponse) -> list[str]:
    images: list[str] = []
    for image_url in (record.image_urls or [])[:4]:
        if image_url.startswith(("http://", "https://")):
            images.append(image_url)
            continue
        data_url = _local_upload_to_data_url(image_url)
        if data_url:
            images.append(data_url)
    return images


def _extract_image_bytes(data: dict[str, Any]) -> tuple[bytes | None, str | None]:
    payload = data.get("data") if isinstance(data.get("data"), dict) else data
    images = payload.get("images") or []
    if not images and payload.get("image"):
        images = [{"url": payload["image"]}]
    if isinstance(images, dict):
        images = [images]
    if not images:
        return None, None

    first = images[0]
    if not isinstance(first, dict):
        return None, None

    b64 = first.get("b64_json") or first.get("base64")
    if b64:
        if "," in b64 and b64.startswith("data:"):
            b64 = b64.split(",", 1)[1]
        return base64.b64decode(b64), None

    return None, first.get("url")


async def generate_travel_poster(record: TravelRecordResponse, style: str) -> str:
    if not settings.vivo_app_key:
        raise HTTPException(status_code=500, detail="后端未配置 VIVO_APP_KEY，无法调用图像生成模型")

    url = f"{_api_root()}/api/v1/image_generation"
    request_id = str(uuid.uuid4())
    payload = {
        "model": settings.vivo_image_model,
        "prompt": _record_prompt(record, style),
        "parameters": {
            "size": "2K",
            "watermark": False,
            "prompt_extend": False,
            "sequential_image_generation": "disabled",
        },
    }
    image_inputs = _image_inputs(record)
    if image_inputs:
        payload["image"] = image_inputs
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {settings.vivo_app_key}",
    }
    params = {
        "module": "aigc",
        "request_id": request_id,
        "system_time": int(time.time()),
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(url, headers=headers, params=params, json=payload)

    try:
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"图像生成接口响应异常：{response.text[:500]}") from exc

    if data.get("code") not in {0, None}:
        raise HTTPException(status_code=502, detail=f"图像生成失败：{data.get('message') or data.get('msg') or data.get('error_msg') or data.get('code')}")

    image_bytes, image_url = _extract_image_bytes(data)
    if image_url:
        try:
            image_bytes = await _download_image(image_url)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"生成图片下载失败：{exc}") from exc

    if not image_bytes:
        raise HTTPException(status_code=502, detail=f"图像生成接口未返回图片：{str(data)[:500]}")

    name = f"{uuid.uuid4().hex}.png"
    path = GENERATED_DIR / name
    path.write_bytes(image_bytes)
    return f"/uploads/generated/{name}"
