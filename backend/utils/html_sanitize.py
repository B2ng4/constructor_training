"""Санитизация HTML заданий (instruction_html) для защиты от XSS."""

from __future__ import annotations

from typing import Optional

import nh3

# Теги, достаточные для QEditor / обучающего текста
_ALLOWED_TAGS = frozenset(
    {
        "a",
        "b",
        "blockquote",
        "br",
        "code",
        "div",
        "em",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "i",
        "li",
        "ol",
        "p",
        "pre",
        "s",
        "strong",
        "sub",
        "sup",
        "u",
        "ul",
        "span",
        "font",
    }
)

# Атрибуты по тегам (nh3 очищает опасные значения в style/url)
_ALLOWED_ATTRIBUTES = {
    "a": {"href", "title", "target", "rel"},
    "span": {"style", "class", "color"},
    "p": {"style", "class"},
    "div": {"style", "class"},
    "font": {"color", "face", "size"},
    "ol": {"start", "type"},
    "li": {"value"},
}


def sanitize_instruction_html(html: Optional[str]) -> Optional[str]:
    if html is None:
        return None
    text = html.strip()
    if not text:
        return None
    cleaned = nh3.clean(
        text,
        tags=set(_ALLOWED_TAGS),
        attributes={k: set(v) for k, v in _ALLOWED_ATTRIBUTES.items()},
        url_schemes={"http", "https", "mailto"},
    )
    out = (cleaned or "").strip()
    return out or None
