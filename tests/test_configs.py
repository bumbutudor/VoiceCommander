"""teste configuratii windows si tello"""

from windows import config as wconfig
from tello import config as tconfig


# --- windows config ---

def test_windows_trigger():
    assert wconfig.TRIGGER == "sistem"
    assert "sistem" in wconfig.TRIGGER_VARIANTS


def test_windows_predicates():
    for pred in ["deschide", "inchide", "acceseaza", "creeaza", "scrie", "ruleaza"]:
        assert pred in wconfig.PREDICATES


def test_windows_apps():
    assert "vscode" in wconfig.APPS
    assert "firefox" in wconfig.APPS


def test_windows_sites():
    assert "gmail" in wconfig.SITES
    assert "moodle" in wconfig.SITES
    assert wconfig.SITES["moodle"] == "https://else.fcim.utm.md/"


def test_windows_context_info():
    info = wconfig.context_info()
    assert isinstance(info, str)
    assert len(info) > 0


# --- tello config ---

def test_tello_trigger():
    assert tconfig.TRIGGER == "tello"
    assert "tello" in tconfig.TRIGGER_VARIANTS


def test_tello_predicates():
    for pred in ["decoleaza", "aterizeaza", "sus", "jos", "stanga",
                 "dreapta", "inainte", "inapoi", "roteste", "fenteaza",
                 "stare", "stop"]:
        assert pred in tconfig.PREDICATES


def test_tello_defaults():
    assert tconfig.DEFAULT_DISTANCE == 50
    assert tconfig.DEFAULT_ANGLE == 90


def test_tello_flip_directions():
    assert set(tconfig.FLIP_DIRECTIONS) == {"l", "r", "f", "b"}


def test_tello_context_info():
    info = tconfig.context_info()
    assert isinstance(info, str)
    assert "sus" in info
    assert "roteste" in info
