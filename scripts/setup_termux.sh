#!/data/data/com.termux/files/usr/bin/bash
# setup VoiceCommander pe Termux (Android ARM)
# ruleaza: bash scripts/setup_termux.sh

set -e

echo "=== 1/6 update pachete termux ==="
pkg update -y && pkg upgrade -y

echo "=== 2/6 instalare pachete sistem ==="
# NUMPY/SCIPY/SKLEARN: le luam prebuilt din termux (evitam compilarea)
pkg install -y \
    python git rust binutils clang make cmake pkg-config \
    portaudio openssl libffi termux-api \
    fftw libsndfile \
    python-numpy python-scipy

echo "=== 3/6 venv python (system-site-packages pentru numpy/scipy) ==="
if [ ! -d .venv ]; then
    python -m venv --system-site-packages .venv
fi
source .venv/bin/activate
pip install --upgrade pip wheel setuptools

echo "=== 4/6 dependinte python (fara faster-whisper/numba) ==="
# faster-whisper/ctranslate2 nu au wheel pe Android - sarim peste
# librosa are dep numba care nu compileaza pe ARM - il instalam fara deps
pip install \
    scikit-learn sounddevice djitellopy google-genai

# librosa dependente (fara numba/llvmlite)
pip install audioread soundfile pooch lazy_loader joblib msgpack decorator typing_extensions
pip install --no-deps librosa

echo "=== 5/6 build whisper.cpp ==="
if [ ! -d "$HOME/whisper.cpp" ]; then
    git clone --depth 1 https://github.com/ggerganov/whisper.cpp "$HOME/whisper.cpp"
fi
cd "$HOME/whisper.cpp"
make -j$(nproc)
# descarca model tiny (cel mai rapid pe telefon)
if [ ! -f models/ggml-tiny.bin ]; then
    bash ./models/download-ggml-model.sh tiny
fi
# linkeaza binary in PATH
mkdir -p "$PREFIX/bin"
ln -sf "$HOME/whisper.cpp/build/bin/whisper-cli" "$PREFIX/bin/whisper-cli" 2>/dev/null \
    || ln -sf "$HOME/whisper.cpp/main" "$PREFIX/bin/whisper-cli"

cd - > /dev/null

echo "=== 6/6 .env pentru termux ==="
if [ ! -f .env ]; then
    cat > .env <<EOF
# config termux/android - whisper.cpp + model tiny
WHISPER_BACKEND=cpp
WHISPER_CPP_MODEL=$HOME/whisper.cpp/models/ggml-tiny.bin
WHISPER_LANGUAGE=ro
# pune cheia gemini aici daca o folosesti, sau ruleaza cu --no-ai
# GEMINI_API_KEY=
EOF
    echo "creat .env (verifica-l)"
fi

echo ""
echo "=== gata! ==="
echo "ruleaza:"
echo "  source .venv/bin/activate"
echo "  termux-wake-lock                       # tine telefonul activ"
echo "  python -m tello --no-ai                # cu drona conectata pe wifi"
