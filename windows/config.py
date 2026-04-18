# configurare windows/wsl

TRIGGER = "sistem"
TRIGGER_VARIANTS = ["sistem", "system", "sisitem"]

PREDICATES = [
    "deschide", "inchide", "acceseaza",
    "creeaza", "scrie", "ruleaza",
    "ajutor", "stop",
]

# aplicatii (ce spui cu vocea -> comanda din sistem)
APPS = {
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "code": "code",
    "mozilla": "firefox",
    "firefox": "firefox",
    "browser": "firefox",
    "chrome": "google-chrome",
    "terminal": "gnome-terminal",
    "consola": "gnome-terminal",
    "fisiere": "nautilus",
    "nautilus": "nautilus",
    "files": "nautilus",
}

# site-uri (ce spui cu vocea -> url)
SITES = {
    "moodle": "https://else.fcim.utm.md/",
    "simu": "https://simu.utm.md/staff/autentificare.php",
    "trello": "https://trello.com",
    "gmail": "https://mail.google.com",
    "drive": "https://drive.google.com",
    "google drive": "https://drive.google.com",
    "github": "https://github.com",
    "youtube": "https://youtube.com",
    "classroom": "https://classroom.google.com",
}

HELP = """
comenzi disponibile:
  sistem deschide <aplicatie>    (vscode, mozilla, terminal...)
  sistem inchide <aplicatie>     (inchide aplicatia)
  sistem acceseaza <site>        (gmail, trello, moodle...)
  sistem creeaza <fisier>        (creeaza un fisier nou)
  sistem scrie <descriere>       (genereaza cod cu ai)
  sistem ruleaza <program>       (ruleaza un fisier/script)
  sistem ajutor                  (afiseaza comenzile)
  sistem stop                    (opreste programul)
"""


def context_info():
    """returneaza info context pentru gemini interpret"""
    apps = ", ".join(APPS.keys())
    sites = ", ".join(SITES.keys())
    return (
        f"APLICATII disponibile: {apps}\n"
        f"SITE-URI disponibile: {sites}\n\n"
        "REGULI SUPLIMENTARE:\n"
        "- corecteaza greseli de transcriere (ex: 'deskide'='deschide', "
        "'vs cod'='vscode', 'mozila'='mozilla', 'gmel'='gmail')\n"
        "- daca comanda e 'scrie', obiectul e descrierea completa a codului"
    )
