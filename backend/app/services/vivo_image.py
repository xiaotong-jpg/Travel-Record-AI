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
视觉身份：真实手工旅行手账。
版式：照片错落倾斜，使用拍立得白边、撕纸边缘和不规则拼贴。
配色：米白、深青蓝、浅棕、鼠尾草绿。
字体：标题为温润宋体，少量手写体点缀。
装饰：纸胶带、邮戳、植物叶片、水彩地标、手绘线条。
禁止：规整网格、霓虹色、黑色胶片边框、极简杂志版式。
""",
    "小红书风": """
视觉身份：明亮时髦的社交媒体旅行分享海报。
版式：照片整齐分区，大图主视觉搭配小图，模块化网格和醒目标签。
配色：奶油白、珊瑚粉、番茄红、明亮黄色，整体高亮清透。
字体：现代粗黑体标题，数字和关键词有明显层级。
装饰：彩色标签、圆角贴纸、星形符号、简洁信息块。
禁止：复古颗粒、暗角、泛黄纸张、水墨、倾斜拍立得和大量植物装饰。
""",
    "清新风": """
视觉身份：轻盈治愈的自然系旅行日记。
版式：大量留白，单张主图或上下错位双图，布局舒展。
配色：纯白、天空蓝、薄荷绿、淡柠檬黄，低饱和透明感。
字体：纤细无衬线字体，标题轻巧简洁。
装饰：透明水彩晕染、细线植物、微小圆点和柔和波纹。
禁止：米黄复古底色、厚重阴影、胶片颗粒、红色标签、密集拼贴。
""",
    "胶片风": """
视觉身份：九十年代复古胶片旅行相册。
版式：横向胶片条、黑色或深棕底片边框、冲印相纸叠放。
配色：焦糖棕、暗红、橄榄绿、暖黄色，明显暖调。
字体：打字机字体或窄体衬线标题。
装饰：胶片齿孔、日期戳、颗粒、漏光、轻微暗角和划痕。
禁止：水彩植物、清新蓝绿、彩色社交标签、纯白极简背景。
""",
    "文艺风": """
视觉身份：安静克制的文学杂志与艺术展览海报。
版式：大面积留白，照片像画作一样居中或偏置，文字采用编辑式纵向节奏。
配色：象牙白、墨黑、灰蓝、少量暗金，低饱和高级感。
字体：高对比宋体或衬线字体，标题纤长，正文简洁。
装饰：细线、页码、短诗、极少量淡墨痕迹。
禁止：卡通贴纸、纸胶带、拍立得边框、彩色标签、密集照片墙和可爱手绘。
""",
}


def _api_root() -> str:
    return settings.vivo_api_base.rstrip("/").removesuffix("/v1")


def _record_prompt(record: TravelRecordResponse, style: str) -> str:
    tags = "、".join((record.mood_tags or [])[:4] + (record.stickers or [])[:3])
    image_count = len(record.image_urls or [])
    normalized_style = style if style in STYLE_PROMPTS else "手账风"
    style_prompt = STYLE_PROMPTS[normalized_style]
    return f"""
生成一张精美的中文旅行日志图片，这是一张“最终可保存分享的图片”，不是网页截图，不要出现按钮、导航栏、输入框。

用户选择的唯一目标风格：{normalized_style}

必须严格执行以下专属视觉规范：
{style_prompt}

画面要求：
1. 竖版旅行日志海报构图。背景、边框、照片布局和装饰必须由上述专属视觉规范决定。
2. 顶部包含中文标题“旅行日志”，但标题字体、颜色、大小和位置必须服从所选风格。
3. 展示日期：{record.travel_date}，地点主标题：{record.place}。
4. 只使用所选风格列出的装饰，禁止套用其他风格的标志性元素。
5. 中部做照片拼贴区域，照片素材只能来自用户上传的参考图片，不允许虚构或补充任何新照片。
6. 可以改变照片裁切、边框、角度和排版，但必须保留用户上传图片中的真实主体与场景。
7. 日志文案参考：{record.memory[:120]}。
8. 心情与标签：{tags or record.mood or "温柔、松弛、旅行记忆"}。
9. 用户上传了 {image_count} 张图片，成品中的所有照片必须来自这些图片；禁止生成新的景点、美食、人物或风景照片。
10. 文字必须清晰可读，排版高级，避免杂乱，不要二维码，不要水印，不要应用按钮。
11. 必须严格体现“{normalized_style}”。这是一次风格重设计，不要沿用其他风格的布局、配色、字体或装饰，不要输出通用手账模板。
12. 图片下方不要添加照片名称、caption、说明文字或手写标注。
13. 重点改造照片周围的页面设计，不要把参考图片本身绘制成其他场景。
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
    for image_url in (record.image_urls or [])[:1]:
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
            "size": "2048x2048",
            "watermark": False,
            "prompt_extend": False,
            "sequential_image_generation": "disabled",
        },
    }
    image_inputs = _image_inputs(record)
    if not image_inputs:
        raise HTTPException(status_code=400, detail="请先上传至少一张旅行图片，再生成 AI 图片日志")
    payload["image"] = image_inputs[0] if len(image_inputs) == 1 else image_inputs
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {settings.vivo_app_key}",
    }
    params = {
        "module": "aigc",
        "request_id": request_id,
        "system_time": int(time.time()),
    }

    response: httpx.Response | None = None
    async with httpx.AsyncClient(timeout=180) as client:
        for attempt in range(2):
            response = await client.post(url, headers=headers, params=params, json=payload)
            if response.status_code not in {500, 502, 503, 504}:
                break
            if attempt == 0:
                params["request_id"] = str(uuid.uuid4())
                params["system_time"] = int(time.time())
                continue

    try:
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        detail = response.text[:500] if response is not None else "empty response"
        raise HTTPException(status_code=502, detail=f"图像生成接口响应异常：{detail}") from exc

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
