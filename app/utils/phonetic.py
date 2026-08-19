from typing import Optional
from metaphone import doublemetaphone, metaphone
from app.utils.normalization import is_latin_script, normalize_title


def compute_phonetic_code(text: str) -> Optional[str]:
    if not text or not is_latin_script(text):
        return None

    norm = normalize_title(text)
    if not norm:
        return None

    words = norm.split()
    codes = []
    
    for word in words:
        try:
            primary, secondary = doublemetaphone(word)
            code = primary or secondary or ""
        except Exception:
            try:
                code = metaphone(word)
            except Exception:
                code = ""
        
        if code:
            codes.append(code)

    if not codes:
        return None

    return " ".join(codes)
