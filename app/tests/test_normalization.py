import pytest
from app.utils.normalization import normalize_title, normalize_domain, is_latin_script
from app.utils.phonetic import compute_phonetic_code


def test_normalize_title():
    assert normalize_title("  Climate  Change—News!  ") == "climate change news"
    assert normalize_title("News & Technology") == "news technology"
    assert normalize_title("  Title 123  ") == "title 123"
    assert normalize_title("my_title_here") == "my title here"
    assert normalize_title("") == ""


def test_normalize_domain():
    assert normalize_domain("news - sports") == "news-sports"
    assert normalize_domain("News - Technology") == "news-technology"
    assert normalize_domain("  business  ") == "business"
    assert normalize_domain("") == "unknown"


def test_is_latin_script():
    assert is_latin_script("Climate Change Today") is True
    assert is_latin_script("12345") is True
    assert is_latin_script("समाचार पत्रिका") is False


def test_compute_phonetic_code():
    code1 = compute_phonetic_code("Climate News")
    code2 = compute_phonetic_code("Klimat Newz")
    assert code1 is not None
    assert code2 is not None
    assert isinstance(code1, str)
    assert compute_phonetic_code("समाचार") is None
