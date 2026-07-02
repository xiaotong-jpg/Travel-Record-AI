from __future__ import annotations

from datetime import date


STYLE_OPTIONS = ["手账风", "明信片风", "朋友圈风", "小红书风", "电影旁白风", "简洁记录风"]
REQUIRED_FIELDS = ["place", "memory", "companion", "mood", "quote", "style"]


def infer_travel_info(message: str, current: dict) -> dict:
    info = dict(current or {})
    text = message.strip()
    if text in {"跳过", "先跳过", "没有", "无"}:
        for field in REQUIRED_FIELDS:
            if field not in info:
                info[field] = ""
                break
        return info

    for style in STYLE_OPTIONS:
        if style in text:
            info["style"] = style

    if "travel_date" not in info:
        info["travel_date"] = date.today().isoformat()
    if "place" not in info:
        for token in ["去了", "在", "到"]:
            if token in text:
                place = text.split(token, 1)[1].split("，", 1)[0].split(",", 1)[0]
                if 1 <= len(place) <= 20:
                    info["place"] = place
                    break
        if "place" not in info and len(text) <= 20:
            info["place"] = text
    elif "memory" not in info:
        info["memory"] = text
    elif "companion" not in info:
        info["companion"] = text
    elif "mood" not in info:
        info["mood"] = text
    elif "quote" not in info:
        info["quote"] = text

    info.setdefault("style", "手账风")
    return info


def missing_fields(info: dict) -> list[str]:
    return [field for field in REQUIRED_FIELDS if field not in info]


def next_question(info: dict) -> str:
    if "place" not in info:
        return "这次旅行去了哪里呀？我来帮你把这段回忆整理成旅行日志。"
    if "memory" not in info:
        return "听起来很有画面感。当天印象最深的事情是什么？"
    if "companion" not in info:
        return "那天是和谁一起去的呢？一个人也可以，我会按你的节奏记录。"
    if "mood" not in info:
        return "当时的心情更接近哪一种？比如松弛、开心、治愈、怀念。"
    if "quote" not in info:
        return "有没有一句特别想留在这页手账里的话？没有也可以说“跳过”。"
    if "style" not in info:
        return "最后想生成什么风格？手账风 / 明信片风 / 朋友圈风 / 小红书风 / 电影旁白风 / 简洁记录风。"
    return "这一刻值得被写进回忆里。我已经整理好了，可以生成旅行手账了。"


def merge_travel_info(current: dict, patch: dict | None) -> dict:
    info = dict(current or {})
    for key, value in (patch or {}).items():
        if key in REQUIRED_FIELDS + ["travel_date"] and value is not None:
            info[key] = str(value).strip()
    info.setdefault("style", "手账风")
    return info