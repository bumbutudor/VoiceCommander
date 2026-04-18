# configurare tello drone

TRIGGER = "tello"
TRIGGER_VARIANTS = [
    "tello", "telo", "tell", "tel",
    "delo", "dello", "de lo", "de lor", "delor",
    "da-l-o", "da lo", "dalo",
    "tel-o", "tel o",
]

PREDICATES = [
    "decoleaza", "aterizeaza",
    "sus", "jos", "stanga", "dreapta",
    "inainte", "inapoi",
    "roteste", "fenteaza",
    "stare", "stop",
]

# distanta default in cm pentru miscari
DEFAULT_DISTANCE = 50

# unghi default in grade pentru rotatii
DEFAULT_ANGLE = 90

# directiile pentru flip (fenteaza)
FLIP_DIRECTIONS = ["l", "r", "f", "b"]

HELP = """
comenzi disponibile:
  tello decoleaza                (decolare automata)
  tello aterizeaza               (aterizare automata)
  tello sus [X]                  (urca X cm, default 50)
  tello jos [X]                  (coboara X cm, default 50)
  tello stanga [X]               (miscare stanga X cm)
  tello dreapta [X]              (miscare dreapta X cm)
  tello inainte [X]              (miscare inainte X cm)
  tello inapoi [X]               (miscare inapoi X cm)
  tello roteste stanga [X]       (roteste X grade ccw, default 90)
  tello roteste dreapta [X]      (roteste X grade cw, default 90)
  tello fenteaza                 (flip random)
  tello stare                    (baterie, inaltime, temp)
  tello stop                     (aterizare de urgenta)
"""


def context_info():
    """returneaza info context pentru gemini interpret"""
    return (
        "OBIECTELE posibile:\n"
        "- pentru miscari: sus, jos, stanga, dreapta, inainte, inapoi "
        "(optional urmat de un numar in cm)\n"
        "- pentru roteste: stanga sau dreapta "
        "(optional urmat de un numar in grade)\n"
        "- pentru fenteaza: fara obiect (flip aleatoriu)\n"
        "- pentru decoleaza/aterizeaza/stare/stop: fara obiect\n\n"
        "REGULI SUPLIMENTARE:\n"
        "- corecteaza greseli de transcriere "
        "(ex: 'decoliaza'='decoleaza', 'aterizeza'='aterizeaza', "
        "'roteshte'='roteste', 'fenteaza'='fenteaza')\n"
        "- daca e un numar in text, e distanta in cm sau unghi in grade\n"
        "- 'sus 100' inseamna 'sus|100', 'roteste stanga 45' inseamna 'roteste|stanga 45'"
    )
