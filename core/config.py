# configurare partajata voicecommander
#
# secretele se citesc din variabile de mediu (sau .env in cwd).
# .env nu se commit-eaza (vezi .gitignore). copiaza .env.example ca punct de plecare.

import os
from pathlib import Path


def _load_dotenv(path=".env"):
    """incarca KEY=VALUE din .env in os.environ (nu suprascrie variabile existente)"""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


_load_dotenv()


# cheia api gemini (gemini flash) - din env
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# model whisper: tiny, base, small, medium, large-v3
# "small" = bun raport viteza/acuratete pentru romana
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "small")
WHISPER_LANGUAGE = os.environ.get("WHISPER_LANGUAGE", "ro")
