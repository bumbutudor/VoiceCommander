"""interpretor local pentru comenzi tello (fara internet/gemini)

mapeaza textul transcris de whisper la (predicat, obiect)
folosind reguli simple pe cuvinte cheie. expune aceeasi
interfata `interpret(text, predicates, context_info="")` ca
`core.ai.AI`, ca sa poata fi folosit drop-in in `Runner`.
"""

import re

from core.utils import normalize


# cuvinte cheie -> predicat canonic
# (acopera variante de transcriere greseala uzuale)
_KEYWORDS = {
    "decoleaza": [
        "decoleaza", "decolare", "decoliaza", "decolhiaza", "decolhează",
        "decolhaza", "decolhază", "decolează",
        "decolat", "decola", "decoleza",
        "decoliasa", "decoliasă", "coliasa", "coliasă",
        "takeoff", "take off", "ridica te", "porneste",
    ],
    "aterizeaza": [
        "aterizeaza", "aterizare", "aterizeza", "aterizhiaza",
        "aterizhaza", "aterizează",
        "aterizat", "ateriza",
        "rizeaza", "rizează", "rizeza",
        "land", "coboara complet",
    ],
    "sus": ["sus", "urca", "ridica", "up"],
    "jos": ["jos", "coboara", "down"],
    "stanga": ["stanga", "left"],
    "dreapta": ["dreapta", "right"],
    "inainte": ["inainte", "fata", "forward", "ahead"],
    "inapoi": ["inapoi", "spate", "back", "inderet", "indaret"],
    "roteste": [
        "roteste", "rotire", "rotatie", "roteshte", "intoarce",
        "invarte", "rotate", "turn",
    ],
    "fenteaza": [
        "fenteaza", "fenta", "flip", "rostogoleste", "rostogol",
        "fenteza", "salt",
    ],
    "stare": ["stare", "status", "baterie", "info"],
    "stop": [
        "stop", "urgenta", "opreste", "opresti", "panica",
        "emergency", "halt",
    ],
}


# cuvinte de directie pentru `roteste`
_DIRECTIONS = {
    "stanga": ["stanga", "left", "ccw"],
    "dreapta": ["dreapta", "right", "cw"],
}


# numerale scrise in cuvinte (cele uzuale pentru cm/grade)
_NUMBER_WORDS = {
    "zero": 0, "unu": 1, "una": 1, "doi": 2, "doua": 2,
    "trei": 3, "patru": 4, "cinci": 5, "sase": 6, "sapte": 7,
    "opt": 8, "noua": 9, "zece": 10, "douazeci": 20, "treizeci": 30,
    "patruzeci": 40, "cincizeci": 50, "saizeci": 60, "saptezeci": 70,
    "optzeci": 80, "nouazeci": 90, "suta": 100, "osuta": 100,
    "douasute": 200, "treisute": 300,
}


def _extract_number(text):
    """extrage primul numar din text (cifre sau cuvant). returneaza str sau ''"""
    m = re.search(r"\d+", text)
    if m:
        return m.group(0)
    for word, val in _NUMBER_WORDS.items():
        if re.search(rf"\b{word}\b", text):
            return str(val)
    return ""


def _find_predicate(text_norm, predicates):
    """gaseste primul predicat din text pe baza cuvintelor cheie"""
    best_pos = None
    best_pred = None
    for pred in predicates:
        for kw in _KEYWORDS.get(pred, [pred]):
            m = re.search(rf"\b{re.escape(kw)}\b", text_norm)
            if m and (best_pos is None or m.start() < best_pos):
                best_pos = m.start()
                best_pred = pred
                break
    return best_pred


def _find_direction(text_norm):
    """gaseste prima directie stanga/dreapta din text"""
    best_pos = None
    best_dir = None
    for direction, words in _DIRECTIONS.items():
        for w in words:
            m = re.search(rf"\b{w}\b", text_norm)
            if m and (best_pos is None or m.start() < best_pos):
                best_pos = m.start()
                best_dir = direction
                break
    return best_dir


class LocalInterpreter:
    """interpretor offline cu aceeasi semnatura ca AI.interpret"""

    def interpret(self, text, predicates, context_info=""):
        if not text:
            return None, None

        text_norm = normalize(text).lower()

        pred = _find_predicate(text_norm, predicates)
        if pred is None:
            return None, None

        num = _extract_number(text_norm)

        if pred == "roteste":
            direction = _find_direction(text_norm) or "stanga"
            obj = direction if not num else f"{direction} {num}"
            return pred, obj

        if pred in ("sus", "jos", "stanga", "dreapta", "inainte", "inapoi"):
            return pred, num

        # decoleaza/aterizeaza/fenteaza/stare/stop - fara obiect
        return pred, ""
