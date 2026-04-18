#!/usr/bin/env python3
"""voicecommander/tello - controleaza drona tello cu vocea"""

import argparse
import os
import sys
import threading

from core.runner import Runner
from tello import config
from tello.commands import execute, _safe_land
from tello.interpreter import LocalInterpreter
from tello.wakeword.detector import WakeWordDetector, MODEL_PATH


# mapare taste -> (predicat, obiect)
KEY_BINDINGS = {
    "d": ("decoleaza", ""),
    "a": ("aterizeaza", ""),
    "w": ("sus", ""),
    "s": ("jos", ""),
    "j": ("stanga", ""),
    "l": ("dreapta", ""),
    "i": ("inainte", ""),
    "k": ("inapoi", ""),
    "e": ("roteste", "dreapta"),
    "r": ("roteste", "stanga"),
    "f": ("fenteaza", ""),
    "x": ("stare", ""),
}


KEYBOARD_HELP = """
TASTE (apasa litera + Enter):
  d  decoleaza        a  aterizeaza
  w  sus              s  jos
  j  stanga           l  dreapta
  i  inainte          k  inapoi
  e  roteste dreapta  r  roteste stanga
  f  fenteaza         x  stare
  q  STOP URGENTA (aterizare imediata + iesire)
"""


def _keyboard_monitor():
    """thread separat: comenzi din tastatura"""
    while True:
        try:
            key = input().strip().lower()
            if not key:
                continue

            if key == "q":
                print("\n[!] ATERIZARE DE URGENTA (tasta q)")
                _safe_land()
                sys.exit(0)

            if key in KEY_BINDINGS:
                predicate, obj = KEY_BINDINGS[key]
                print(f"[tastatura] {predicate} {obj}".rstrip())
                try:
                    result = execute(predicate, obj)
                    print(f"[result] {result}")
                except Exception as e:
                    print(f"[eroare] {e}")
            elif key == "?":
                print(KEYBOARD_HELP)
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(prog="tello", description=__doc__)
    parser.add_argument(
        "-n", "--no-ai",
        action="store_true",
        help="ruleaza fara gemini (folosesc doar interpretorul local offline)",
    )
    args = parser.parse_args()

    # porneste monitorizare tastatura in background
    kb_thread = threading.Thread(target=_keyboard_monitor, daemon=True)
    kb_thread.start()

    # incarca wake word detector daca exista modelul antrenat
    wake_word = None
    if os.path.exists(MODEL_PATH):
        try:
            wake_word = WakeWordDetector()
            print(f"[wake word] activ (prag={wake_word.threshold})")
        except Exception as e:
            print(f"[wake word] indisponibil: {e}")
    else:
        print(f"[wake word] model lipsa ({MODEL_PATH}) - folosesc trigger text")

    if args.no_ai:
        print("[ai] dezactivat (--no-ai) - folosesc doar interpretorul local")

    runner = Runner(
        name="tello",
        trigger=config.TRIGGER,
        trigger_variants=config.TRIGGER_VARIANTS,
        predicates=config.PREDICATES,
        context_info=config.context_info(),
        execute_fn=execute,
        help_text=config.HELP + KEYBOARD_HELP,
        wake_word=wake_word,
        interpreter=LocalInterpreter(),
        use_ai=not args.no_ai,
    )
    runner.run()


if __name__ == "__main__":
    main()
