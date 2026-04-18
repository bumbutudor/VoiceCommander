"""comenzi drone tello via djitellopy"""

import atexit
import random
import re
import signal

from djitellopy import Tello

from tello import config
from core.utils import normalize


_drone = None


def _safe_land():
    """aterizare de siguranta - apelata automat la exit/crash/signal"""
    global _drone
    if _drone is not None:
        try:
            print("\n[!] aterizare de siguranta...")
            _drone.land()
            print("[!] aterizat.")
        except Exception:
            try:
                _drone.emergency()
            except Exception:
                pass


def _signal_handler(sig, frame):
    """handler pentru SIGINT/SIGTERM"""
    _safe_land()
    raise SystemExit(0)


# inregistreaza aterizare automata la exit + semnale
atexit.register(_safe_land)
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def get_drone():
    """returneaza instanta drone conectata"""
    global _drone
    if _drone is None:
        print("conectare la tello...")
        _drone = Tello()
        _drone.connect()
        bat = _drone.get_battery()
        print(f"tello conectat (baterie: {bat}%)")
    return _drone


def _extract_number(text, default):
    """extrage un numar din text sau returneaza default"""
    nums = re.findall(r"\d+", text)
    if nums:
        val = int(nums[0])
        return max(20, min(val, 500))
    return default


def execute(predicate, obj, ai=None):
    """executa comanda drone: predicat + obiect"""
    pred = normalize(predicate).strip()

    actions = {
        "decoleaza": cmd_takeoff,
        "aterizeaza": cmd_land,
        "sus": cmd_up,
        "jos": cmd_down,
        "stanga": cmd_left,
        "dreapta": cmd_right,
        "inainte": cmd_forward,
        "inapoi": cmd_back,
        "roteste": cmd_rotate,
        "fenteaza": cmd_flip,
        "stare": cmd_status,
        "stop": cmd_emergency,
    }

    handler = actions.get(pred)
    if handler:
        return handler(obj)

    return f"comanda necunoscuta: {pred}"


# --- comenzi drone ---


def cmd_takeoff(_obj):
    """decolare"""
    drone = get_drone()
    drone.takeoff()
    return "decolat"


def cmd_land(_obj):
    """aterizare"""
    drone = get_drone()
    drone.land()
    return "aterizat"


def cmd_up(obj):
    """urca X cm"""
    dist = _extract_number(obj, config.DEFAULT_DISTANCE)
    drone = get_drone()
    drone.move_up(dist)
    return f"sus {dist}cm"


def cmd_down(obj):
    """coboara X cm"""
    dist = _extract_number(obj, config.DEFAULT_DISTANCE)
    drone = get_drone()
    drone.move_down(dist)
    return f"jos {dist}cm"


def cmd_left(obj):
    """miscare stanga X cm"""
    dist = _extract_number(obj, config.DEFAULT_DISTANCE)
    drone = get_drone()
    drone.move_left(dist)
    return f"stanga {dist}cm"


def cmd_right(obj):
    """miscare dreapta X cm"""
    dist = _extract_number(obj, config.DEFAULT_DISTANCE)
    drone = get_drone()
    drone.move_right(dist)
    return f"dreapta {dist}cm"


def cmd_forward(obj):
    """miscare inainte X cm"""
    dist = _extract_number(obj, config.DEFAULT_DISTANCE)
    drone = get_drone()
    drone.move_forward(dist)
    return f"inainte {dist}cm"


def cmd_back(obj):
    """miscare inapoi X cm"""
    dist = _extract_number(obj, config.DEFAULT_DISTANCE)
    drone = get_drone()
    drone.move_back(dist)
    return f"inapoi {dist}cm"


def cmd_rotate(obj):
    """roteste stanga/dreapta X grade"""
    obj_norm = normalize(obj).lower()
    angle = _extract_number(obj, config.DEFAULT_ANGLE)
    drone = get_drone()

    if "dreapta" in obj_norm:
        drone.rotate_clockwise(angle)
        return f"rotit dreapta {angle}°"
    else:
        # default: stanga
        drone.rotate_counter_clockwise(angle)
        return f"rotit stanga {angle}°"


def cmd_flip(_obj):
    """flip aleatoriu (fenteaza)"""
    direction = random.choice(config.FLIP_DIRECTIONS)
    names = {"l": "stanga", "r": "dreapta", "f": "inainte", "b": "inapoi"}
    drone = get_drone()
    drone.flip(direction)
    return f"fenta {names[direction]}"


def cmd_status(_obj):
    """afiseaza starea dronei"""
    drone = get_drone()
    bat = drone.get_battery()
    height = drone.get_height()
    temp = drone.get_temperature()
    print(f"  baterie: {bat}%")
    print(f"  inaltime: {height}cm")
    print(f"  temperatura: {temp}°C")
    return "stare afisata"


def cmd_emergency(_obj):
    """aterizare de urgenta"""
    drone = get_drone()
    try:
        drone.land()
    except Exception:
        drone.emergency()
    return "stop executat"
