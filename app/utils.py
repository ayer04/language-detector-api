
import re
from typing import Optional
import pycountry

_letters_re = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-žḀ-ỿ]")

def clean_text(t: str) -> str:
    return t.strip()

def is_garbage_text(t: str) -> bool:
    # Weniger als 3 Buchstaben oder fast nur Sonderzeichen/Zahlen → unbestimmt
    letters = _letters_re.findall(t or "")
    return len(letters) < 3

def iso3_from_alpha2(alpha2: str) -> Optional[str]:
    if not alpha2 or alpha2 == "und":
        return None
    try:
        lang = pycountry.languages.get(alpha_2=alpha2)
        if lang and hasattr(lang, "alpha_3"):
            return lang.alpha_3
    except Exception:
        pass
    return None
