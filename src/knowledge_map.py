import logging
import tempfile
from collections import Counter

import numpy as np
import spacy
from pyvis.network import Network
from sklearn.manifold import TSNE

from .models import Article

logger = logging.getLogger(__name__)

nlp = spacy.load("ja_ginza", exclude=["compound_splitter"])

CATEGORY_COLORS = [
    "#2EBFB3", "#4A7C59", "#D4A574", "#1A5F7A", "#8ECFCC",
    "#E8855A", "#7B61FF", "#E8B84B", "#5AA0E8", "#B05AE8",
]


class KnowledgeMap:
    def build_graph(self, articles: list[Article]) -> str:
        if len(articles) < 2:
            return "<p>記事が少なすぎて地図を生成できませんでした。</p>"

        # Step 1: タイトル + タグ を ja_ginza でベクトル化
        embeddings = np.array([
            nlp(f"{a.title} {' '.join(a.tags)}").vector
            for a in articles
        ])

        # Step 2: TSNE で 2D 圧縮
        perplexity = min(30, len(articles) - 1)
        reducer = TSNE(n_components=2, perplexity=perplexity, random_state=42)
        coords = reducer.fit_transform(embeddings)

        scale = 600
        coords = (coords - coords.mean(axis=0)) / (coords.std(axis=0) + 1e-8) * scale

        # Step 3: GiNZA でキーワード抽出 → カテゴリー化
        article_keywords: list[set[str]] = []
        keyword_freq: Counter = Counter()

        for article in articles:
            text = article.title + " " + " ".join(article.tags)
            doc = nlp(text)
            words = {
                token.text for token in doc
                if token.pos_ in ("NOUN", "PROPN") and len(token.text) >= 2
            }
            logger.info("[%s] キーワード: %s", article.slug, sorted(words))
            article_keywords.append(words)
            for w in words:
                keyword_freq[w] += 1

        # 出現頻度上位のキーワードをカテゴリーラベルとして使用
        top_keywords = [kw for kw, _ in keyword_freq.most_common(len(CATEGORY_COLORS))]
        logger.info("カテゴリーキーワード: %s", top_keywords)

        color_map = {kw: CATEGORY_COLORS[i] for i, kw in enumerate(top_keywords)}

        def get_color(words: set[str]) -> str:
            for kw in top_keywords:
                if kw in words:
                    return color_map[kw]
            return "#AAAAAA"

        # Step 4: pyvis グラフ構築（物理演算オフ・エッジなし）
        net = Network(height="580px", width="100%", bgcolor="#FAF7F2", font_color="#1A5F7A")
        net.toggle_physics(False)

        for i, article in enumerate(articles):
            x, y = float(coords[i][0]), float(coords[i][1])
            color = get_color(article_keywords[i])
            label = article.title if len(article.title) <= 20 else article.title[:19] + "…"
            tooltip = f"{article.title}\nタグ: {', '.join(article.tags) or 'なし'}"
            net.add_node(i, label=label, x=x, y=y, color=color, title=tooltip, size=18, physics=False)

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            net.save_graph(f.name)

        with open(f.name, "r", encoding="utf-8") as f:
            return f.read()
