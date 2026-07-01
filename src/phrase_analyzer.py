import random
import re
from collections import Counter


class PhraseAnalyzer:
    HABIT_PATTERNS = [
        r"ですね",
        r"ですよね",
        r"かもしれません",
        r"かも(?:ね|です)?",
        r"ですが",
        r"つまり",
        r"要するに",
        r"なるほど",
        r"実は",
        r"ちなみに",
        r"もちろん",
        r"基本的に",
        r"個人的に",
        r"正直",
        r"意外と",
    ]

    KATAKANA_RE = re.compile(r"[ァ-ヴー]{3,}")
    INTERESTING_RE = re.compile(r"[ァ-ヴー]{3,}|[a-zA-Z]{4,}(?:的|感|力|系)?|[^\s。、！？\n]{5,}(?:感|力|系|的)")

    def find_habits(self, texts: list[str]) -> list[tuple[str, int]]:
        counter: Counter = Counter()
        for text in texts:
            for pattern in self.HABIT_PATTERNS:
                matches = re.findall(pattern, text)
                if matches:
                    counter[matches[0]] += len(matches)
        return counter.most_common(10)

    def find_syntax_patterns(self, texts: list[str]) -> list[tuple[str, int]]:
        counts = {
            "コードブロック (```)": 0,
            "見出し (#)": 0,
            "箇条書き (-)": 0,
            "番号リスト (1.)": 0,
            "リンク ([text](url))": 0,
        }
        for text in texts:
            counts["コードブロック (```)"] += len(re.findall(r"```", text)) // 2
            counts["見出し (#)"] += len(re.findall(r"^#{1,6}\s", text, re.MULTILINE))
            counts["箇条書き (-)"] += len(re.findall(r"^- ", text, re.MULTILINE))
            counts["番号リスト (1.)"] += len(re.findall(r"^\d+\.\s", text, re.MULTILINE))
            counts["リンク ([text](url))"] += len(re.findall(r"\[.+?\]\(https?://.+?\)", text))
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)

    def find_interesting_phrases(self, texts: list[str]) -> list[str]:
        candidates = []
        for text in texts:
            matches = self.INTERESTING_RE.findall(text)
            candidates.extend(matches)
        unique = list(dict.fromkeys(candidates))
        return random.sample(unique, min(10, len(unique)))
