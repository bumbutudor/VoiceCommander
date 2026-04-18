"""teste tello/commands.py cu mock drone"""

from unittest.mock import patch, MagicMock

import tello.commands as tello_cmds
from tello.commands import (
    execute,
    _extract_number,
    cmd_takeoff,
    cmd_land,
    cmd_up,
    cmd_down,
    cmd_left,
    cmd_right,
    cmd_forward,
    cmd_back,
    cmd_rotate,
    cmd_flip,
    cmd_status,
    cmd_emergency,
    _safe_land,
)


def _mock_drone():
    """creaza un mock drone si il pune in modulul tello.commands"""
    drone = MagicMock()
    drone.get_battery.return_value = 80
    drone.get_height.return_value = 100
    drone.get_temperature.return_value = 45
    tello_cmds._drone = drone
    return drone


# --- _extract_number ---

def test_extract_number_gasit():
    assert _extract_number("100", 50) == 100


def test_extract_number_default():
    assert _extract_number("", 50) == 50
    assert _extract_number("abc", 50) == 50


def test_extract_number_clamp_min():
    assert _extract_number("5", 50) == 20  # min 20


def test_extract_number_clamp_max():
    assert _extract_number("999", 50) == 500  # max 500


def test_extract_number_in_text():
    assert _extract_number("stanga 75", 50) == 75


# --- execute dispatch ---

def test_execute_decoleaza():
    drone = _mock_drone()
    result = execute("decoleaza", "")
    assert result == "decolat"
    drone.takeoff.assert_called_once()


def test_execute_aterizeaza():
    drone = _mock_drone()
    result = execute("aterizeaza", "")
    assert result == "aterizat"
    drone.land.assert_called_once()


def test_execute_necunoscut():
    _mock_drone()
    result = execute("zboara", "")
    assert "necunoscuta" in result


# --- comenzi individuale ---

def test_cmd_takeoff():
    drone = _mock_drone()
    assert cmd_takeoff("") == "decolat"
    drone.takeoff.assert_called_once()


def test_cmd_land():
    drone = _mock_drone()
    assert cmd_land("") == "aterizat"
    drone.land.assert_called_once()


def test_cmd_up_default():
    drone = _mock_drone()
    result = cmd_up("")
    assert result == "sus 50cm"
    drone.move_up.assert_called_once_with(50)


def test_cmd_up_custom():
    drone = _mock_drone()
    result = cmd_up("100")
    assert result == "sus 100cm"
    drone.move_up.assert_called_once_with(100)


def test_cmd_down():
    drone = _mock_drone()
    result = cmd_down("30")
    assert result == "jos 30cm"
    drone.move_down.assert_called_once_with(30)


def test_cmd_left():
    drone = _mock_drone()
    result = cmd_left("")
    assert result == "stanga 50cm"
    drone.move_left.assert_called_once_with(50)


def test_cmd_right():
    drone = _mock_drone()
    result = cmd_right("80")
    assert result == "dreapta 80cm"
    drone.move_right.assert_called_once_with(80)


def test_cmd_forward():
    drone = _mock_drone()
    result = cmd_forward("")
    assert result == "inainte 50cm"
    drone.move_forward.assert_called_once_with(50)


def test_cmd_back():
    drone = _mock_drone()
    result = cmd_back("200")
    assert result == "inapoi 200cm"
    drone.move_back.assert_called_once_with(200)


def test_cmd_rotate_stanga_default():
    drone = _mock_drone()
    result = cmd_rotate("stanga")
    assert "stanga" in result
    assert "90" in result
    drone.rotate_counter_clockwise.assert_called_once_with(90)


def test_cmd_rotate_dreapta_custom():
    drone = _mock_drone()
    result = cmd_rotate("dreapta 45")
    assert "dreapta" in result
    assert "45" in result
    drone.rotate_clockwise.assert_called_once_with(45)


def test_cmd_flip():
    drone = _mock_drone()
    result = cmd_flip("")
    assert "fenta" in result
    drone.flip.assert_called_once()


def test_cmd_status(capsys):
    drone = _mock_drone()
    result = cmd_status("")
    assert result == "stare afisata"
    output = capsys.readouterr().out
    assert "80%" in output
    assert "100cm" in output
    assert "45" in output


def test_cmd_emergency():
    drone = _mock_drone()
    result = cmd_emergency("")
    assert "stop" in result
    drone.land.assert_called_once()


def test_cmd_emergency_land_fails():
    drone = _mock_drone()
    drone.land.side_effect = Exception("timeout")
    result = cmd_emergency("")
    assert "stop" in result
    drone.emergency.assert_called_once()


# --- safe_land ---

def test_safe_land_cu_drone():
    drone = _mock_drone()
    _safe_land()
    drone.land.assert_called()


def test_safe_land_fara_drone():
    tello_cmds._drone = None
    _safe_land()  # nu trebuie sa dea eroare


def test_safe_land_land_esueaza():
    drone = _mock_drone()
    drone.land.side_effect = Exception("err")
    _safe_land()  # trebuie sa apeleze emergency
    drone.emergency.assert_called()
