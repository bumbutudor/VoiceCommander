"""teste tello/interpreter.py - parser local offline"""

from tello.interpreter import LocalInterpreter
from tello import config


def _interp(text):
    return LocalInterpreter().interpret(text, config.PREDICATES)


def test_decoleaza():
    assert _interp("decoleaza") == ("decoleaza", "")


def test_decoleaza_greseala():
    assert _interp("decoliaza acum") == ("decoleaza", "")


def test_decoleaza_greseala_h():
    assert _interp("decolhiaza!") == ("decoleaza", "")


def test_decoleaza_de_coliasa():
    assert _interp("de coliasa.") == ("decoleaza", "")


def test_decoleaza_de_coliasa_diacritice():
    assert _interp("de coliasă.") == ("decoleaza", "")


def test_decoleaza_decoliasa():
    assert _interp("decoliasa.") == ("decoleaza", "")


def test_aterizeaza_a_te_rizeaza():
    assert _interp("a te rizează!") == ("aterizeaza", "")


def test_aterizeaza():
    assert _interp("aterizeaza te rog") == ("aterizeaza", "")


def test_sus_fara_numar():
    assert _interp("sus") == ("sus", "")


def test_sus_cu_numar():
    assert _interp("sus 100") == ("sus", "100")


def test_urca_sinonim():
    pred, obj = _interp("urca 80")
    assert pred == "sus"
    assert obj == "80"


def test_jos():
    assert _interp("coboara 50") == ("jos", "50")


def test_inainte():
    assert _interp("inainte 30") == ("inainte", "30")


def test_inapoi():
    assert _interp("inapoi") == ("inapoi", "")


def test_stanga():
    assert _interp("stanga 60") == ("stanga", "60")


def test_dreapta_diacritice():
    assert _interp("dreapta 40") == ("dreapta", "40")


def test_roteste_dreapta():
    pred, obj = _interp("roteste dreapta 90")
    assert pred == "roteste"
    assert "dreapta" in obj and "90" in obj


def test_roteste_stanga_default():
    pred, obj = _interp("roteste stanga")
    assert pred == "roteste"
    assert obj == "stanga"


def test_roteste_fara_directie_default_stanga():
    pred, obj = _interp("roteste 45")
    assert pred == "roteste"
    assert "stanga" in obj and "45" in obj


def test_fenteaza():
    assert _interp("fenteaza") == ("fenteaza", "")


def test_flip_sinonim():
    assert _interp("flip") == ("fenteaza", "")


def test_stare():
    assert _interp("stare") == ("stare", "")


def test_baterie_sinonim():
    assert _interp("baterie") == ("stare", "")


def test_stop():
    assert _interp("stop") == ("stop", "")


def test_text_neclar():
    assert _interp("salut ce faci") == (None, None)


def test_text_gol():
    assert _interp("") == (None, None)


def test_diacritice_normalizate():
    pred, obj = _interp("rotește dreapta 90")
    assert pred == "roteste"
    assert "dreapta" in obj


def test_numar_in_cuvant():
    pred, obj = _interp("sus o suta")
    assert pred == "sus"
    # "suta" -> 100
    assert obj == "100"
