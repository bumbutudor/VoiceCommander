"""teste windows/commands.py cu mock subprocess"""

from unittest.mock import patch, MagicMock

from windows.commands import execute, cmd_open, cmd_close, cmd_access, cmd_create


def test_execute_deschide():
    with patch("windows.commands.cmd_open", return_value="ok") as m:
        result = execute("deschide", "vscode")
        m.assert_called_once_with("vscode")
        assert result == "ok"


def test_execute_inchide():
    with patch("windows.commands.cmd_close", return_value="ok") as m:
        result = execute("inchide", "firefox")
        m.assert_called_once_with("firefox")


def test_execute_acceseaza():
    with patch("windows.commands.cmd_access", return_value="ok") as m:
        result = execute("acceseaza", "gmail")
        m.assert_called_once_with("gmail")


def test_execute_comanda_necunoscuta():
    result = execute("zboara", "sus")
    assert "necunoscuta" in result


def test_execute_scrie_trimite_ai():
    mock_ai = MagicMock()
    with patch("windows.commands.cmd_write", return_value="ok") as m:
        execute("scrie", "hello world", ai=mock_ai)
        m.assert_called_once_with("hello world", mock_ai)


def test_cmd_open_app():
    with patch("subprocess.Popen") as mock_popen:
        result = cmd_open("vscode")
        assert "deschis" in result
        mock_popen.assert_called_once()


def test_cmd_open_site_redirect():
    """deschide gmail -> redirect la cmd_access"""
    with patch("windows.commands.open_url") as mock_url:
        result = cmd_open("gmail")
        assert "browser" in result
        mock_url.assert_called_once()


def test_cmd_close_app():
    with patch("subprocess.run") as mock_run:
        result = cmd_close("firefox")
        assert "inchis" in result
        mock_run.assert_called_once()


def test_cmd_access_site_cunoscut():
    with patch("windows.commands.open_url") as mock_url:
        result = cmd_access("gmail")
        assert "browser" in result
        mock_url.assert_called_once_with("https://mail.google.com")


def test_cmd_access_site_necunoscut_cu_punct():
    with patch("windows.commands.open_url") as mock_url:
        result = cmd_access("example.com")
        assert "browser" in result
        mock_url.assert_called_once_with("https://example.com")


def test_cmd_access_site_necunoscut_fara_punct():
    result = cmd_access("ceva random")
    assert "necunoscut" in result


def test_cmd_create_fisier(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("subprocess.Popen"):
        result = cmd_create("test")
        assert "creat" in result
        assert (tmp_path / "test.py").exists()


def test_cmd_create_cu_extensie(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("subprocess.Popen"):
        result = cmd_create("data.json")
        assert "creat" in result
        assert (tmp_path / "data.json").exists()
