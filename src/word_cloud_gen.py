from __future__ import annotations

import glob
import io
import os

import spacy
from wordcloud import WordCloud

from .models import Article

_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux/Docker
    "/usr/share/fonts/noto-cjk/NotoSansCJKjp-Regular.otf",
]
# macOS: ヒラギノ (path varies by OS version)
_FONT_CANDIDATES += glob.glob("/System/Library/Fonts/ヒラギノ*.ttc")
_FONT_CANDIDATES += glob.glob("/System/Library/Fonts/Hiragino*.ttc")


def _find_cjk_font() -> str | None:
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None

_LAGOON_COLORS = ["#2EBFB3", "#1A5F7A", "#4A7C59", "#8ECFCC", "#D4A574", "#4A90D9"]


def _lagoon_color_func(*args, **kwargs) -> str:
    import random
    return random.choice(_LAGOON_COLORS)


class WordCloudGen:
    def __init__(self) -> None:
        self._nlp = spacy.load("ja_ginza", exclude=["compound_splitter"])

    def generate(self, articles: list[Article]) -> bytes:
        words: list[str] = []
        for article in articles:
            doc = self._nlp(article.title)
            for token in doc:
                if token.pos_ in ("NOUN", "PROPN") and len(token.text) >= 2:
                    words.append(token.text)

        if not words:
            words = ["記事", "なし"]

        text = " ".join(words)

        font_path = _find_cjk_font()

        wc = WordCloud(
            font_path=font_path,
            width=800,
            height=400,
            background_color="#FAF7F2",
            color_func=_lagoon_color_func,
            max_words=80,
            prefer_horizontal=0.9,
        ).generate(text)

        buf = io.BytesIO()
        wc.to_image().save(buf, format="PNG")
        buf.seek(0)
        return buf.read()
