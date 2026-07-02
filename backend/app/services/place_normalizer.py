from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.core.config import settings
from app.services.vivo_chat_client import chat_completion, extract_json_object


@dataclass(frozen=True)
class NormalizedPlace:
    city: str
    normalized_place: str
    confidence: str = "medium"
    source: str = "local"
    places: list[str] = field(default_factory=list)
    place_regions: list[dict[str, str]] = field(default_factory=list)
    is_multi_city: bool = False


LANDMARK_CITY_MAP: dict[str, str] = {
    "曲院风荷": "杭州",
    "断桥残雪": "杭州",
    "断桥": "杭州",
    "苏堤": "杭州",
    "白堤": "杭州",
    "雷峰塔": "杭州",
    "灵隐寺": "杭州",
    "飞来峰": "杭州",
    "西溪湿地": "杭州",
    "西湖": "杭州",
    "湖滨": "杭州",
    "河坊街": "杭州",
    "清河坊": "杭州",
    "玉龙雪山": "丽江",
    "虎跳峡": "丽江",
    "束河古镇": "丽江",
    "丽江古城": "丽江",
    "鸣沙山": "敦煌",
    "月牙泉": "敦煌",
    "莫高窟": "敦煌",
    "玉门关": "敦煌",
    "阳关": "敦煌",
    "什刹海": "北京",
    "故宫": "北京",
    "天坛": "北京",
    "颐和园": "北京",
    "外滩": "上海",
    "豫园": "上海",
    "武康路": "上海",
}

PROVINCE_CITY_HINTS: dict[str, list[str]] = {
    "云南": ["昆明", "大理", "丽江", "香格里拉", "西双版纳", "腾冲"],
    "浙江": ["杭州", "宁波", "温州", "绍兴", "湖州", "嘉兴", "舟山"],
    "江苏": ["南京", "苏州", "无锡", "扬州", "镇江", "常州"],
    "四川": ["成都", "乐山", "绵阳", "都江堰", "九寨沟"],
    "广东": ["广州", "深圳", "珠海", "佛山", "汕头"],
    "甘肃": ["兰州", "敦煌", "嘉峪关", "张掖"],
    "青海": ["西宁", "海西", "玉树", "果洛"],
}

CITY_PROVINCE_MAP: dict[str, str] = {
    "北京": "北京",
    "上海": "上海",
    "天津": "天津",
    "重庆": "重庆",
    "杭州": "浙江",
    "宁波": "浙江",
    "温州": "浙江",
    "绍兴": "浙江",
    "湖州": "浙江",
    "嘉兴": "浙江",
    "舟山": "浙江",
    "南京": "江苏",
    "苏州": "江苏",
    "无锡": "江苏",
    "扬州": "江苏",
    "镇江": "江苏",
    "常州": "江苏",
    "昆明": "云南",
    "大理": "云南",
    "丽江": "云南",
    "香格里拉": "云南",
    "西双版纳": "云南",
    "腾冲": "云南",
    "成都": "四川",
    "乐山": "四川",
    "绵阳": "四川",
    "都江堰": "四川",
    "九寨沟": "四川",
    "广州": "广东",
    "深圳": "广东",
    "珠海": "广东",
    "佛山": "广东",
    "汕头": "广东",
    "兰州": "甘肃",
    "敦煌": "甘肃",
    "嘉峪关": "甘肃",
    "张掖": "甘肃",
    "西宁": "青海",
    "海西": "青海",
    "玉树": "青海",
    "果洛": "青海",
    "青海": "青海",
}

PROVINCE_NAMES = set(PROVINCE_CITY_HINTS.keys()) | {"北京", "上海", "天津", "重庆"}
DIRECT_CITY_SUFFIXES = ("市", "区", "县")
PLACE_SPLIT_RE = re.compile(r"[·\s,，、/|-]+")
CITY_MENTION_RE = re.compile(r"([\u4e00-\u9fff]{2,8}?)(?:市|区|县)")


def raw_place_name(place: str | None) -> str:
    value = str(place or "").strip()
    return next((part.strip() for part in PLACE_SPLIT_RE.split(value) if part.strip()), "")


def normalize_city_name(city: str) -> str:
    city = str(city or "").strip()
    return re.sub(r"(市|区|县)$", "", city) or city


def unique_places(values: list[str]) -> list[str]:
    seen: set[str] = set()
    places: list[str] = []
    for value in values:
        city = normalize_city_name(value)
        if not city or city in seen or city in {"未知城市", "未命名旅行地"}:
            continue
        seen.add(city)
        places.append(city)
    return places


def region_for_place(place: str) -> dict[str, str]:
    city = normalize_city_name(place)
    if city in PROVINCE_NAMES and city not in CITY_PROVINCE_MAP:
        return {"province": city, "city": city}
    return {"province": CITY_PROVINCE_MAP.get(city, city), "city": city}


def unique_regions(values: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    regions: list[dict[str, str]] = []
    for value in values:
        province = normalize_city_name(value.get("province") or "")
        city = normalize_city_name(value.get("city") or province)
        if not province and city:
            province = CITY_PROVINCE_MAP.get(city, city)
        key = (province, city)
        if not province or not city or key in seen:
            continue
        seen.add(key)
        regions.append({"province": province, "city": city})
    return regions


def extract_local_places(text: str | None) -> list[str]:
    value = str(text or "")
    places: list[str] = []

    for landmark, city in LANDMARK_CITY_MAP.items():
        if landmark in value:
            places.append(city)

    for province, cities in PROVINCE_CITY_HINTS.items():
        province_cities = [city for city in cities if city in value]
        if province_cities:
            places.extend(province_cities)
        elif province in value:
            places.append(province)

    for match in CITY_MENTION_RE.finditer(value):
        places.append(match.group(1))

    for part in PLACE_SPLIT_RE.split(value):
        part = part.strip()
        if part.endswith(DIRECT_CITY_SUFFIXES):
            places.append(part)

    return unique_places(places)


def normalize_place_local(place: str | None, context: str | None = None) -> NormalizedPlace:
    raw = raw_place_name(place)
    text = "\n".join(part for part in [str(place or ""), str(context or "")] if part)
    places = extract_local_places(text)

    if not raw and not places:
        return NormalizedPlace(city="未知城市", normalized_place="未知地点", confidence="low", places=[])

    if not places and raw.endswith(DIRECT_CITY_SUFFIXES):
        places = [normalize_city_name(raw)]

    if not places and raw:
        places = [normalize_city_name(raw)]

    regions = unique_regions([region_for_place(value) for value in places])
    city = places[0] if places else "未知城市"
    normalized_place = raw or "、".join(places) or "未知地点"
    confidence = "high" if len(places) > 1 else ("medium" if raw.endswith(DIRECT_CITY_SUFFIXES) else "low")
    return NormalizedPlace(
        city=city,
        normalized_place=normalized_place,
        confidence=confidence,
        places=places,
        place_regions=regions,
        is_multi_city=len(places) > 1,
    )


async def normalize_place(place: str | None, context: str | None = None) -> NormalizedPlace:
    local = normalize_place_local(place, context)
    if not settings.vivo_app_key:
        return local

    prompt = f"""请判断这篇中文旅行日志涉及哪些省份和城市，并只返回 JSON。
要求：
1. 单城市日志返回一个 place_regions 项，例如玉龙雪山必须识别为 {{"province":"云南", "city":"丽江"}}。
2. 如果用户提到多个城市或多省旅程，place_regions 返回所有涉及的省份/城市。
3. 如果只提到省份没有具体城市，city 可等于 province。
4. 如果地点是景点、街区、公园、寺庙、商圈，请推断它所在省份和城市。
5. 不要返回国家名。
6. 如果无法判断，province 和 city 都返回输入地点本身，confidence 返回 low。

返回格式：
{{"city":"", "normalized_place":"", "places":[], "place_regions":[{{"province":"", "city":""}}], "is_multi_city": false, "confidence":"high|medium|low"}}

用户填写地点：{place}
日志上下文：{context or "未提供"}
"""
    try:
        content = await chat_completion(
            [
                {"role": "system", "content": "你是中文旅行地点归一化助手，只输出 JSON。"},
                {"role": "user", "content": prompt},
            ],
            max_tokens=600,
            temperature=0.1,
        )
        data = extract_json_object(content)
        ai_regions = unique_regions([item for item in (data.get("place_regions") or []) if isinstance(item, dict)])
        ai_places = unique_places([str(item) for item in (data.get("places") or [])])
        places = ai_places or [region["city"] for region in ai_regions] or local.places or [local.city]
        regions = ai_regions or unique_regions([region_for_place(value) for value in places]) or local.place_regions
        city = normalize_city_name(str(data.get("city") or places[0] or local.city))
        normalized_place = str(data.get("normalized_place") or raw_place_name(place) or "、".join(places) or local.normalized_place)
        confidence = str(data.get("confidence") or "medium")
        if confidence not in {"high", "medium", "low"}:
            confidence = "medium"
        return NormalizedPlace(
            city=city,
            normalized_place=normalized_place,
            confidence=confidence,
            source="ai",
            places=places,
            place_regions=regions,
            is_multi_city=bool(data.get("is_multi_city")) or len(places) > 1,
        )
    except Exception:
        return local


def normalize_place_json(place: str | None) -> dict[str, object]:
    normalized = normalize_place_local(place)
    return {
        "city": normalized.city,
        "normalized_place": normalized.normalized_place,
        "confidence": normalized.confidence,
        "source": normalized.source,
        "places": normalized.places,
        "place_regions": normalized.place_regions,
        "is_multi_city": normalized.is_multi_city,
    }