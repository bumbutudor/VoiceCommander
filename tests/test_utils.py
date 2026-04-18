"""teste core/utils.py"""

from core.utils import normalize


def test_normalize_diacritice():
    assert normalize("ă") == "a"
    assert normalize("â") == "a"
    assert normalize("î") == "i"
    assert normalize("ș") == "s"
    assert normalize("ț") == "t"


def test_normalize_cuvinte():
    assert normalize("deschide") == "deschide"
    assert normalize("accesează") == "acceseaza"
    assert normalize("închide") == "inchide"
    assert normalize("creează") == "creeaza"
    assert normalize("rulează") == "ruleaza"


def test_normalize_text_lung():
    assert normalize("Ștefan își închide ușa") == "Stefan isi inchide usa"


def test_normalize_fara_diacritice():
    assert normalize("abc 123") == "abc 123"


def test_normalize_empty():
    assert normalize("") == ""


def test_normalize_cedilla_variants():
    # variante vechi (cedilla) vs noi (comma below)
    assert normalize("ş") == "s"
    assert normalize("ţ") == "t"
