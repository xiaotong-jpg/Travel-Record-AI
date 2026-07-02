from __future__ import annotations

import json

from app.core.config import settings
from app.services.travel_memory import infer_travel_info, missing_fields, next_question
from app.services.vivo_chat_client import chat_completion, extract_json_object


CHAT_SYSTEM_PROMPT = """你是“AI 旅行搭子”，不是表单机器人。
你的目标是陪用户慢慢回忆旅行，提供情绪价值，同时悄悄整理生成旅行日志所需的信息。

说话方式：
- 温柔、具体、有共情，像真的在听用户讲旅行。
- 不要每次都机械问“去了哪里/和谁/心情是什么”。
- 如果用户已经讲了画面，要先回应画面和情绪，再自然追问一个最需要补充的问题。
- 一次最多问 1 个问题。
- 可以承接用户的话，比如“这个细节很适合写进手账”。
- 不要输出 Markdown。

你必须只返回 JSON：
{
  "reply": "给用户看的自然回复",
  "travel_info_patch": {
    "place": "",
    "travel_date": "YYYY-MM-DD 或空",
    "memory": "",
    "companion": "",
    "mood": "",
    "quote": "",
    "style": "手账风/明信片风/朋友圈风/小红书风/电影旁白风/简洁记录风"
  }
}
只填写本轮能确定的信息，不确定就不要放这个字段。
"""


def _fallback_reply(message: str, current_info: dict) -> tuple[str, dict]:
    info = infer_travel_info(message, current_info)
    return next_question(info), info


async def chat_as_travel_agent(message: str, history: list[dict], current_info: dict) -> tuple[str, dict]:
    if not settings.vivo_app_key:
        return _fallback_reply(message, current_info)

    compact_history = history[-10:]
    prompt = f"""当前已整理的信息：
{json.dumps(current_info or {}, ensure_ascii=False)}

最近对话：
{json.dumps(compact_history, ensure_ascii=False)}

用户最新消息：{message}

请生成一次自然、有情绪价值的回复，并提取本轮新信息。
"""
    try:
        content = await chat_completion(
            [
                {"role": "system", "content": CHAT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=900,
            temperature=0.85,
        )
        data = extract_json_object(content)
        patch = data.get("travel_info_patch") or {}
        info = dict(current_info or {})
        for key, value in patch.items():
            if value not in {None, ""}:
                info[key] = str(value).strip()
        info.setdefault("style", "手账风")

        missing = missing_fields(info)
        reply = str(data.get("reply") or "")
        if not reply:
            reply = next_question(info)
        elif missing:
            # Keep the agent useful if it only empathizes but forgets to ask for needed info.
            reply = f"{reply}\n\n{next_question(info)}"
        else:
            reply = f"{reply}\n\n信息已经差不多了，想生成的话可以点下面的“生成手账”。"
        return reply, info
    except Exception:
        return _fallback_reply(message, current_info)