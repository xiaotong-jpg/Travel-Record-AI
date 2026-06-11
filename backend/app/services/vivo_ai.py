from __future__ import annotations

from datetime import date

from fastapi import HTTPException

from app.core.config import settings
from app.schemas.travel import TravelAIResult, TravelGenerateRequest
from app.services.vivo_chat_client import chat_completion, extract_json_object


SYSTEM_PROMPT = """你是 AI 旅行记忆助手，擅长把零散旅行信息整理成有画面感、有情绪价值的中文旅行日志。
整体风格是新中式轻文艺 + 数字旅行手账：低饱和自然色、留白、温柔、克制、有陪伴感。
你必须只返回 JSON，不要输出 Markdown，不要解释。
JSON 结构必须是：
{
  "title": "",
  "content": "",
  "location_desc": "",
  "mood_tags": [],
  "stickers": [],
  "share_text": "",
  "timeline_items": [],
  "section_blocks": [],
  "image_layout_suggestions": []
}
"""


def build_travel_prompt(payload: TravelGenerateRequest, image_urls: list[str] | None = None) -> str:
    image_text = "、".join(image_urls or []) or "未上传"
    return f"""请根据以下用户旅行信息生成旅行日志。

旅行地点：{payload.place}
旅行时间：{payload.travel_date}
同行人：{payload.companion or "未填写"}
当天心情：{payload.mood or "未填写"}
印象最深的事情：{payload.memory}
想记录的一句话：{payload.quote or "未填写"}
日志风格：{payload.style}
上传图片：{image_text}

要求：
1. title 简短、有记忆点。
2. content 写成 2-4 段，像真实旅行手账，不要空泛。
3. location_desc 用一句话描述地点气质。
4. mood_tags 返回 3-5 个中文短标签。
5. stickers 返回 3-6 个适合旅行卡片的贴纸标签。
6. share_text 适合朋友圈/小红书分享，温柔但不过度营销。
7. timeline_items 返回 2-4 个时间轴节点，每项包含 time/title/text。
8. section_blocks 返回 3-5 个手账排版块，每项包含 type/title/text。
9. image_layout_suggestions 根据上传图片数量给出拼贴建议。
"""


def _to_ai_result(data: dict) -> TravelAIResult:
    def normalize_blocks(items: list | None) -> list[dict]:
        normalized: list[dict] = []
        for item in items or []:
            if isinstance(item, dict):
                normalized.append(item)
            else:
                normalized.append({"text": str(item)})
        return normalized

    return TravelAIResult(
        title=str(data.get("title") or "一页旅行记忆"),
        content=str(data.get("content") or ""),
        location_desc=str(data.get("location_desc") or ""),
        mood_tags=list(data.get("mood_tags") or []),
        stickers=list(data.get("stickers") or []),
        share_text=str(data.get("share_text") or ""),
        timeline_items=normalize_blocks(data.get("timeline_items")),
        section_blocks=normalize_blocks(data.get("section_blocks")),
        image_layout_suggestions=normalize_blocks(data.get("image_layout_suggestions")),
    )


def mock_travel_result(payload: TravelGenerateRequest, image_urls: list[str] | None = None) -> TravelAIResult:
    companion = f"和{payload.companion}" if payload.companion else "一个人"
    quote = f"\n\n那句想留下的话是：{payload.quote}" if payload.quote else ""
    image_count = len(image_urls or [])
    return TravelAIResult(
        title=f"{payload.place}，把今天轻轻收好",
        content=(
            f"{payload.travel_date}，{companion}去了{payload.place}。{payload.memory}，像一枚安静的书签，"
            f"夹在这段旅程里。\n\n"
            f"那天的心情是{payload.mood or '柔软的'}，风景没有催促人向前，只是把时间放慢了一点。"
            f"等以后再翻到这一页，应该还能想起当时的光、路边的声音和心里很轻的那一下。{quote}"
        ),
        location_desc=f"{payload.place}像一页低饱和的旅行手账，安静、有风，也有值得回看的细节。",
        mood_tags=["松弛", "温柔", "有光", payload.mood or "被治愈"],
        stickers=["晚风", "路标", "手账贴", "今日收藏"],
        share_text=f"在{payload.place}把日子过慢一点，也把回忆收得认真一点。",
        timeline_items=[
            {"time": "抵达", "title": "把脚步交给这座城", "text": f"从{payload.place}开始，今天有了被记录的理由。"},
            {"time": "傍晚", "title": "最深的画面", "text": payload.memory},
            {"time": "回看", "title": "留给未来的一句话", "text": payload.quote or "这一刻值得被写进回忆里。"},
        ],
        section_blocks=[
            {"type": "note", "title": "地点气质", "text": f"{payload.place}有一种慢下来的温柔。"},
            {"type": "journal", "title": "今日手账", "text": payload.memory},
            {"type": "quote", "title": "一句话", "text": payload.quote or "把今天轻轻收好。"},
        ],
        image_layout_suggestions=[
            {"type": "film-strip" if image_count > 2 else "postcard", "text": f"已上传 {image_count} 张照片，适合做成胶片拼贴。"}
        ],
    )


async def call_vivo_travel(payload: TravelGenerateRequest, image_urls: list[str] | None = None) -> tuple[TravelAIResult, str]:
    if not settings.vivo_app_key:
        if settings.vivo_mock_when_no_key:
            result = mock_travel_result(payload, image_urls)
            return result, result.model_dump_json(ensure_ascii=False)
        raise HTTPException(status_code=500, detail="后端未配置 VIVO_APP_KEY")

    content = await chat_completion(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_travel_prompt(payload, image_urls)},
        ],
        max_tokens=2048,
        temperature=0.7,
    )
    return _to_ai_result(extract_json_object(content)), content


async def call_vivo_year_summary(records: list[dict]) -> str:
    if not records:
        return "今年还没有留下旅行记录。先生成一篇旅行日志，再让 AI 帮你把一年慢慢整理成册。"

    if not settings.vivo_app_key and settings.vivo_mock_when_no_key:
        places = "、".join(record["place"] for record in records[:6])
        return f"这一年的旅行记忆从{places}开始，被整理成了几页有光的手账。你走过的地方不只是坐标，也是情绪被安放的时刻。"

    content = await chat_completion(
        [
            {"role": "system", "content": "你是 AI 旅行记忆助手，请用温柔、克制的新中式旅行手账文风生成年度旅行总结。"},
            {"role": "user", "content": f"根据这些旅行记录生成一段 200 字以内的年度旅行总结：{records}"},
        ],
        max_tokens=1024,
        temperature=0.7,
    )
    return content.strip()


def today_as_date(value: str | None) -> date:
    if not value:
        return date.today()
    return date.fromisoformat(value[:10])
