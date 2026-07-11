from __future__ import annotations

import io
import os

import spacy
from wordcloud import WordCloud

from .models import Article

_NOTO_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

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

        font_path = _NOTO_FONT_PATH if os.path.exists(_NOTO_FONT_PATH) else None

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
