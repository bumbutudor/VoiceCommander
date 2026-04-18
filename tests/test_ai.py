"""teste core/ai.py cu mock gemini"""

from unittest.mock import patch, MagicMock

from core.ai import AI


def _mock_ai(response_text):
    """creaza AI cu gemini mock care returneaza response_text"""
    with patch("core.ai.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = response_text
        mock_client.models.generate_content.return_value = mock_response

        ai = AI()
        return ai


def test_interpret_comanda_corecta():
    ai = _mock_ai("deschide|firefox")
    pred, obj = ai.interpret("deschide firefox", ["deschide", "inchide"], "")
    assert pred == "deschide"
    assert obj == "firefox"


def test_interpret_comanda_corectata():
    ai = _mock_ai("deschide|mozilla")
    pred, obj = ai.interpret("deskide mozila", ["deschide", "inchide"], "")
    assert pred == "deschide"
    assert obj == "mozilla"


def test_interpret_neclar():
    ai = _mock_ai("neclar")
    pred, obj = ai.interpret("bla bla bla", ["deschide"], "")
    assert pred is None
    assert obj is None


def test_interpret_fara_pipe():
    ai = _mock_ai("nu inteleg")
    pred, obj = ai.interpret("xyz", ["deschide"], "")
    assert pred is None
    assert obj is None


def test_interpret_tello_decoleaza():
    ai = _mock_ai("decoleaza|")
    pred, obj = ai.interpret("decoliaza", ["decoleaza", "aterizeaza"], "")
    assert pred == "decoleaza"
    assert obj == ""


def test_interpret_tello_sus_100():
    ai = _mock_ai("sus|100")
    pred, obj = ai.interpret("sus o suta", ["sus", "jos"], "")
    assert pred == "sus"
    assert obj == "100"


def test_generate_code():
    ai = _mock_ai("print('hello')")
    code = ai.generate_code("printeaza hello")
    assert "print" in code


def test_generate_code_strips_markdown():
    ai = _mock_ai("```python\nprint('hello')\n```")
    code = ai.generate_code("printeaza hello")
    assert "```" not in code
    assert "print" in code
