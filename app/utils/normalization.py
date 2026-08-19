import re
import unicodedata


def normalize_title(text: str) -> str:
    if not text:
        return ""

    # 1. Unicode NFKC normalization
    normalized = unicodedata.normalize("NFKC", text)

    # 2. Casefold
    normalized = normalized.casefold()

    # 3. Replace common punctuation & symbols with space (including underscores)
    # Keep alphanumeric characters and convert punctuation/symbols to space
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)

    # 4. Collapse multiple internal whitespaces and strip
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized


def normalize_domain(text: str) -> str:
    if not text:
        return "unknown"

    # Lowercase & strip
    domain = text.strip().lower()

    # Convert domain spacing around hyphens e.g. "news - sports" -> "news-sports"
    domain = re.sub(r"\s*-\s*", "-", domain)

    # Collapse multiple spaces into single hyphen or space
    domain = re.sub(r"\s+", "-", domain)

    return domain


def is_latin_script(text: str) -> bool:
    if not text:
        return False
    
    latin_chars = 0
    total_alpha = 0

    for char in text:
        if char.isalpha():
            total_alpha += 1
            # Check script block / unicode category for Latin
            try:
                name = unicodedata.name(char)
                if "LATIN" in name:
                    latin_chars += 1
            except ValueError:
                pass

    if total_alpha == 0:
        return True

    return (latin_chars / total_alpha) >= 0.8
