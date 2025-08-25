
import os
import math
from typing import List, Tuple, Dict
from .utils import clean_text, is_garbage_text

# Optionale Engines
_HAS_FASTTEXT = False
try:  # pragma: no cover
    import fasttext  # type: ignore
    _HAS_FASTTEXT = True
except Exception:
    _HAS_FASTTEXT = False

import langid  # type: ignore
from langdetect import detect_langs  # type: ignore


def _softmax(scores: List[float]) -> List[float]:
    if not scores:
        return scores
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    total = sum(exps)
    if total == 0:
        return [0.0 for _ in scores]
    return [e / total for e in exps]


class Detector:
    def __init__(self):
        self.engine_name = "ensemble"
        self.ft_model = None
        if _HAS_FASTTEXT:
            model_path = os.getenv("FASTTEXT_MODEL_PATH", "models/lid.176.ftz")
            if os.path.exists(model_path):
                try:
                    self.ft_model = fasttext.load_model(model_path)  # type: ignore
                    self.engine_name = "fasttext"
                except Exception:
                    self.ft_model = None

    def detect(self, text: str):
        t = clean_text(text)
        if is_garbage_text(t):
            return {
                "language": "und",
                "confidence": 0.0,
                "alternatives": [],
                "engine": self.engine_name,
            }
        if self.ft_model is not None:
            return self._detect_fasttext(t)
        return self._detect_ensemble(t)

    def detect_batch(self, items: List[str]):
        return [self.detect(t) for t in items]

    # --- Engines ---
    def _detect_fasttext(self, t: str):
        labels, probs = self.ft_model.predict(t, k=3)  # type: ignore
        # Labels wie __label__en
        langs = [lab.replace("__label__", "") for lab in labels[0]] if labels and labels[0] else []
        confs = probs[0] if probs and probs[0] is not None else []
        if not langs:
            return {"language": "und", "confidence": 0.0, "alternatives": [], "engine": "fasttext"}
        primary = langs[0]
        primary_conf = float(confs[0]) if confs else 0.0
        alts = []
        for l, p in zip(langs[1:], confs[1:]):
            alts.append({"language": l, "confidence": float(p)})
        return {"language": primary, "confidence": primary_conf, "alternatives": alts, "engine": "fasttext"}

    def _detect_ensemble(self, t: str):
        # langdetect
        try:
            ld_candidates = detect_langs(t)  # returns like [LangProb('en',0.99), ...]
            ld_map: Dict[str, float] = {c.lang: float(c.prob) for c in ld_candidates}
        except Exception:
            ld_map = {}

        # langid (scores sind Log-Prob-ähnlich; nutzen Softmax zur Normalisierung)
        li_rank: List[Tuple[str, float]] = langid.rank(t)
        li_langs = [l for l, s in li_rank]
        li_scores = [float(s) for l, s in li_rank]
        li_probs = _softmax(li_scores)
        li_map: Dict[str, float] = {l: p for l, p in zip(li_langs, li_probs)}

        # Kombinieren (Gewichtung langdetect etwas höher)
        combined: Dict[str, float] = {}
        for l, p in ld_map.items():
            combined[l] = combined.get(l, 0.0) + 0.6 * p
        for l, p in li_map.items():
            combined[l] = combined.get(l, 0.0) + 0.4 * p

        # Normalisieren
        total = sum(combined.values()) or 1.0
        for k in list(combined.keys()):
            combined[k] = combined[k] / total

        # Sortiert
        ordered = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        if not ordered:
            return {"language": "und", "confidence": 0.0, "alternatives": [], "engine": "langid+langdetect"}
        primary, pconf = ordered[0]
        alts = [{"language": l, "confidence": float(c)} for l, c in ordered[1:4]]
        return {"language": primary, "confidence": float(pconf), "alternatives": alts, "engine": "langid+langdetect"}
