"""teste core/runner.py - find_trigger logic"""

from core.runner import Runner


def _make_runner(**kwargs):
    defaults = dict(
        name="test",
        trigger="sistem",
        trigger_variants=["sistem", "system", "sisitem"],
        predicates=["deschide", "inchide"],
        context_info="",
        execute_fn=lambda p, o, ai=None: None,
        help_text="",
    )
    defaults.update(kwargs)
    return Runner(**defaults)


# --- find_trigger ---

def test_trigger_gasit():
    r = _make_runner()
    assert r.find_trigger("sistem deschide vscode") == "deschide vscode"


def test_trigger_variant():
    r = _make_runner()
    assert r.find_trigger("system deschide firefox") == "deschide firefox"


def test_trigger_absent():
    r = _make_runner()
    assert r.find_trigger("salut ce faci") is None


def test_trigger_trailing_letter():
    """sistema -> sterge litera 'a' lipita"""
    r = _make_runner()
    result = r.find_trigger("sistema deschide vscode")
    assert result == "deschide vscode"


def test_trigger_trailing_u():
    """sistemu deschide -> sterge 'u'"""
    r = _make_runner()
    result = r.find_trigger("sistemu deschide chrome")
    assert result == "deschide chrome"


def test_trigger_strip_punctuatie():
    r = _make_runner()
    result = r.find_trigger("sistem, deschide moodle")
    assert result == "deschide moodle"


def test_trigger_doar_trigger():
    r = _make_runner()
    result = r.find_trigger("sistem")
    assert result == ""


def test_trigger_tello():
    r = _make_runner(
        trigger="tello",
        trigger_variants=["tello", "tell", "delo"],
    )
    assert r.find_trigger("tello decoleaza") == "decoleaza"


def test_trigger_tello_variant():
    r = _make_runner(
        trigger="tello",
        trigger_variants=["tello", "tell", "delo"],
    )
    result = r.find_trigger("delo sus 100")
    assert result is not None
    assert "sus" in result
