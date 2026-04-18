"""parsarea si executia comenzilor vocale - windows/wsl"""

import subprocess
import os

from windows import config
from core.utils import normalize


# detecteaza wsl
def _is_wsl():
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False

_WSL = _is_wsl()


def open_url(url):
    """deschide url in browser (compatibil wsl)"""
    if _WSL:
        subprocess.Popen(
            ["cmd.exe", "/c", "start", url.replace("&", "^&")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        import webbrowser
        webbrowser.open(url)


# fisierul curent pe care lucram
_current_file = None


def get_current_file():
    return _current_file


def set_current_file(path):
    global _current_file
    _current_file = path


def execute(predicate, obj, ai=None):
    """executa comanda: predicat + obiect"""
    pred = normalize(predicate).strip()

    actions = {
        "deschide": cmd_open,
        "inchide": cmd_close,
        "acceseaza": cmd_access,
        "creeaza": cmd_create,
        "creaza": cmd_create,
        "scrie": cmd_write,
        "ruleaza": cmd_run,
        "ajutor": cmd_help,
        "stop": cmd_stop,
        "opreste": cmd_stop,
    }

    handler = actions.get(pred)
    if handler:
        if pred == "scrie":
            return handler(obj, ai)
        return handler(obj)

    return f"comanda necunoscuta: {pred}"


# --- implementari comenzi ---


def cmd_open(obj):
    """deschide o aplicatie (sau site daca obiectul e un site cunoscut)"""
    obj_norm = normalize(obj).lower().strip()

    for name in config.SITES:
        if obj_norm in normalize(name) or normalize(name) in obj_norm:
            return cmd_access(obj)

    for name, cmd in config.APPS.items():
        if obj_norm in normalize(name) or normalize(name) in obj_norm:
            try:
                subprocess.Popen(
                    [cmd],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return f"{name} deschis"
            except FileNotFoundError:
                if _WSL:
                    try:
                        subprocess.Popen(
                            ["cmd.exe", "/c", "start", cmd],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        return f"{name} deschis"
                    except FileNotFoundError:
                        pass
                return f"eroare: '{cmd}' nu a fost gasit in sistem"

    return f"aplicatie necunoscuta: {obj}"


def cmd_close(obj):
    """inchide o aplicatie"""
    obj_norm = normalize(obj).lower().strip()

    for name, cmd in config.APPS.items():
        if obj_norm in normalize(name) or normalize(name) in obj_norm:
            subprocess.run(
                ["pkill", "-f", cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return f"{name} inchis"

    return f"aplicatie necunoscuta: {obj}"


def cmd_access(obj):
    """deschide un site in browser"""
    obj_norm = normalize(obj).lower().strip()

    for name, url in config.SITES.items():
        if obj_norm in normalize(name) or normalize(name) in obj_norm:
            open_url(url)
            return f"{name} deschis in browser"

    if "." in obj and " " not in obj.strip():
        url = obj.strip()
        if not url.startswith("http"):
            url = "https://" + url
        open_url(url)
        return f"{url} deschis in browser"

    return f"site necunoscut: {obj}"


def cmd_create(obj):
    """creeaza un fisier nou"""
    obj = obj.strip()
    for word in ["fisier", "fișier", "fişier", "file"]:
        obj = obj.replace(word, "").strip()

    if not obj:
        return "eroare: specifica numele fisierului"

    filename = obj.replace(" ", "_")
    if "." not in filename:
        filename += ".py"

    path = os.path.abspath(filename)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("")

    set_current_file(path)

    subprocess.Popen(
        ["code", "-r", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return f"fisier creat: {filename}"


_FILE_EXTENSIONS = {
    ".py", ".js", ".ts", ".html", ".css", ".java",
    ".cpp", ".c", ".sh", ".rs", ".rb", ".go", ".txt",
    ".json", ".yaml", ".yml", ".xml", ".md", ".sql",
}


def cmd_write(obj, ai=None):
    """scrie cod in fisierul curent folosind gemini"""
    if ai is None:
        return "eroare: gemini nu este configurat"

    target = get_current_file()

    obj = obj.strip()
    obj_lower = obj.lower().lstrip(".,!?;: ")
    for noise in ["cod ", "code ", "cod,", "code,", "cod.", "code."]:
        if obj_lower.startswith(noise):
            obj = obj[len(noise):].strip()
            break

    words = obj.split()
    for i, w in enumerate(words):
        clean = w.rstrip(".,!?;:")
        ext = os.path.splitext(clean)[1]
        if ext in _FILE_EXTENSIONS and "/" not in w:
            target = os.path.abspath(clean)
            obj = " ".join(words[:i] + words[i + 1:])
            break

    obj = obj.strip()
    if obj.startswith("in "):
        obj = obj[3:].strip()

    if not obj.strip():
        return "eroare: descrie ce sa scriu"

    lang = "python"
    if target:
        ext_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".html": "html", ".css": "css", ".java": "java",
            ".cpp": "c++", ".c": "c", ".sh": "bash", ".rs": "rust",
            ".rb": "ruby", ".go": "go",
        }
        ext = os.path.splitext(target)[1]
        lang = ext_map.get(ext, "python")

    print(f"  generez cod {lang}...")
    code = ai.generate_code(obj, language=lang, filename=target)

    if not target:
        target = os.path.abspath("output.py")

    with open(target, "a") as f:
        f.write(code + "\n")

    set_current_file(target)

    subprocess.Popen(
        ["code", "-r", target],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    lines = code.count("\n") + 1
    return f"{lines} linii scrise in {os.path.basename(target)}"


def cmd_run(obj):
    """ruleaza un program/script in terminalul vs code"""
    obj = obj.strip()

    if not obj or obj in ("asta", "curent", "fisierul", "cod", "code", "codul"):
        current = get_current_file()
        if current and os.path.isfile(current):
            obj = current
        else:
            return "eroare: nu exista fisier curent de rulat"

    if not os.path.isfile(obj):
        full = os.path.abspath(obj)
        if os.path.isfile(full):
            obj = full
        else:
            return f"fisier negasit: {obj}"

    ext = os.path.splitext(obj)[1]
    runners = {
        ".py": f"python3 {obj}",
        ".sh": f"bash {obj}",
        ".js": f"node {obj}",
        ".ts": f"npx ts-node {obj}",
    }
    run_cmd = runners.get(ext, f"python3 {obj}")

    subprocess.Popen(
        ["code", "-r", obj],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print(f"  rulare: {run_cmd}")
    print("  " + "-" * 30)
    result = subprocess.run(run_cmd, shell=True, timeout=30)
    print("  " + "-" * 30)
    return f"rulat: {os.path.basename(obj)} (cod iesire: {result.returncode})"


def cmd_help(_obj):
    """afiseaza comenzile disponibile"""
    apps = ", ".join(config.APPS.keys())
    sites = ", ".join(config.SITES.keys())
    current = get_current_file()
    cf = os.path.basename(current) if current else "niciun fisier"
    print(f"\n  fisier curent: {cf}\n  aplicatii: {apps}\n  site-uri: {sites}\n")
    return "ajutor afisat"


def cmd_stop(_obj):
    """opreste programul"""
    raise SystemExit(0)
