# VoiceCommander

Comenzi vocale in limba romana pentru:

- **Tello** — controleaza drona DJI/Ryze Tello cu vocea (cu wake word custom "tello")
- **Windows** — comenzi de sistem (deschide aplicatii, etc.)

Stack: `faster-whisper` (STT) + `gemini-2.0-flash` (parser comenzi, optional) + interpretor local offline (fallback) + `scikit-learn` (wake word) + `djitellopy` (drona).

---

## Cerinte

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (sau `pip` + `venv`)
- microfon
- (optional) drona Tello pentru modulul `tello`

## Instalare

```bash
git clone https://github.com/bumbutudor/VoiceCommander.git
cd VoiceCommander
uv sync
```

Configureaza cheia API Gemini (optional — fara ea, modulul `tello` merge cu `--no-ai`):

```bash
cp .env.example .env
# editeaza .env si pune cheia ta de la https://aistudio.google.com/apikey
```

---

## Tello — control drona cu vocea

### Conectare la drona

1. Porneste drona Tello.
2. Conecteaza-te pe wifi-ul ei (`TELLO-XXXXXX`).
3. Pe wifi-ul dronei nu ai internet — vezi sectiunea "fara internet" mai jos.

### Rulare

```bash
uv run python -m tello              # cu gemini (necesita internet)
uv run python -m tello --no-ai      # doar interpretor local (recomandat pe wifi-ul dronei)
```

### Flow

1. App-ul calibreaza microfonul.
2. Asculta continuu dupa wake word-ul **"tello"** (model custom antrenat local).
3. Cand detecteaza "tello", inregistreaza urmatoarea comanda cu Whisper.
4. Comanda transcrisa e parsata fie de Gemini, fie de interpretorul local offline.
5. Comanda e trimisa dronei.

### Comenzi disponibile

```
tello decoleaza                (decolare automata)
tello aterizeaza               (aterizare automata)
tello sus [X]                  (urca X cm, default 50)
tello jos [X]                  (coboara X cm, default 50)
tello stanga [X]               (miscare stanga X cm)
tello dreapta [X]              (miscare dreapta X cm)
tello inainte [X]              (miscare inainte X cm)
tello inapoi [X]               (miscare inapoi X cm)
tello roteste stanga [X]       (X grade ccw, default 90)
tello roteste dreapta [X]      (X grade cw, default 90)
tello fenteaza                 (flip random)
tello stare                    (baterie, inaltime, temp)
tello stop                     (aterizare de urgenta)
```

### Taste de siguranta

In timp ce app-ul ruleaza, poti apasa litera + Enter:

```
d  decoleaza        a  aterizeaza
w  sus              s  jos
j  stanga           l  dreapta
i  inainte          k  inapoi
e  roteste dreapta  r  roteste stanga
f  fenteaza         x  stare
q  STOP URGENTA (aterizare imediata + iesire)
```

Plus: `Ctrl+C` declanseaza aterizare automata de siguranta.

### Fara internet (pe wifi-ul dronei)

Cand esti conectat la `TELLO-XXXXXX`, nu ai internet, deci Gemini si descarcarea modelelor Whisper esueaza.

- **Whisper** — la prima rulare descarca modelul (necesita internet o data); apoi merge offline din cache.
- **Gemini** — foloseste `--no-ai` pentru a sari peste el complet:
  ```bash
  uv run python -m tello --no-ai
  ```
  Interpretorul local din [tello/interpreter.py](tello/interpreter.py) parseaza comenzile pe baza de cuvinte cheie (acopera variante de transcriere uzuale: `decolhiaza`, `de coliasa`, `urca`, `flip`, etc.).

Daca rulezi fara `--no-ai` si Gemini esueaza, fallback-ul local intra automat.

---

## Wake word custom

Modulul detecteaza cuvantul "tello" cu un model `LogisticRegression` antrenat pe MFCC.

### Re-antrenare cu propria voce

```bash
# 1. Inregistreaza ~20 sample-uri pozitive ("tello")
uv run python -m tello.wakeword.record tello 20

# 2. Inregistreaza ~100 sample-uri negative (alte cuvinte, comenzi, zgomote)
uv run python -m tello.wakeword.record negative 100

# 3. Antreneaza
uv run python -m tello.wakeword.train

# 4. Testeaza standalone
uv run python -m tello.wakeword.detector
```

Sample-urile se salveaza in `data/wakeword/{tello,negative}/`. Modelul antrenat: `data/wakeword_model.pkl` (se incarca automat).

Pragul de detectie e configurat la `0.97` in [tello/wakeword/detector.py](tello/wakeword/detector.py); creste-l daca ai false positives, scade-l daca rateaza detectii.

---

## Mobil — Termux pe Android

Poti rula app-ul direct pe telefon, conectat la wifi-ul dronei. Nu ai nevoie de laptop.

### Cerinte

- **Termux** instalat din F-Droid sau GitHub releases (NU din Play Store, e abandonat)
- **Termux:API** instalat din F-Droid (pentru permisiuni microfon)

### Instalare

```bash
# in Termux
pkg install git -y
termux-setup-storage    # accepta permisiunile

git clone https://github.com/bumbutudor/VoiceCommander.git
cd VoiceCommander

bash scripts/setup_termux.sh
```

Scriptul:
- instaleaza `python`, `portaudio`, `clang`, `cmake`, etc.
- creeaza `.venv` si instaleaza dependintele Python (fara `faster-whisper` care nu compileaza pe ARM)
- compileaza `whisper.cpp` din sursa si descarca modelul `ggml-tiny`
- creeaza `.env` cu `WHISPER_BACKEND=cpp`

### Rulare pe telefon

```bash
# conecteaza-te la wifi-ul TELLO-XXXXXX din Settings
source .venv/bin/activate
termux-wake-lock                          # nu lasa telefonul sa adoarma
python -m tello --no-ai                   # zboara
```

### Backend whisper configurabil

Pe PC se foloseste `faster-whisper` (default), pe Termux `whisper.cpp` (subprocess). Configurabil prin env (vezi [.env.example](.env.example)):

```
WHISPER_BACKEND=cpp                                  # sau "faster" pe PC
WHISPER_CPP_BIN=whisper-cli
WHISPER_CPP_MODEL=~/whisper.cpp/models/ggml-tiny.bin
```

### Limitari Termux

- Latenta: model `tiny` ~3-5s pe telefoane mid-range. Acceptabil pentru comenzi scurte.
- Microfonul cere permisiune Termux:API la prima rulare.
- Daca ecranul se inchide, foloseste `termux-wake-lock`.
- Nu poti folosi internet si drona simultan (drona e singurul wifi disponibil).

---

## Windows — control sistem

```bash
uv run python -m windows
```

Vezi [windows/config.py](windows/config.py) pentru lista de comenzi. Necesita Gemini configurat.

---

## Teste

```bash
uv run pytest -q
```

100 teste, ruleaza in <2s.

---

## Arhitectura

```
core/
  runner.py       # bucla principala partajata: listen -> trigger -> interpret -> execute
  voice.py        # captura microfon + faster-whisper STT
  ai.py           # client Gemini (parser comenzi)
  config.py       # incarca .env, expune GEMINI_API_KEY, WHISPER_MODEL
tello/
  __main__.py     # entry point + argparse + thread tastatura
  commands.py     # implementare comenzi drona (djitellopy)
  config.py       # trigger, predicates, defaults
  interpreter.py  # parser local offline (fallback la gemini)
  wakeword/
    record.py     # tool inregistrare sample-uri
    train.py      # antrenare LogisticRegression pe MFCC
    detector.py   # detectie real-time + wait_for_trigger()
    features.py   # extragere MFCC
windows/
  __main__.py     # entry point
  commands.py     # implementare comenzi sistem
  config.py
data/
  wakeword/       # sample-uri audio (ignorate de git: *.wav)
  wakeword_model.pkl
```

`Runner` e generic — primeste un `execute_fn`, optional `wake_word` si `interpreter`, si poate fi reutilizat pentru orice device nou.

---

## Licenta

MIT
