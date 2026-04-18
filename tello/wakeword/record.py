"""inregistreaza mostre vocale pentru antrenare wake word"""

import os
import sys
import termios
import time
from collections import deque

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from tello.wakeword.features import SAMPLE_RATE, CLIP_DURATION


def flush_stdin():
    try:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except Exception:
        pass


DATA_DIR = "data/wakeword"


def record_session(label, n_samples):
    out_dir = os.path.join(DATA_DIR, label)
    os.makedirs(out_dir, exist_ok=True)
    existing_files = [f for f in os.listdir(out_dir) if f.endswith(".wav")]
    if existing_files:
        max_idx = max(int(f.split(".")[0]) for f in existing_files if f.split(".")[0].isdigit())
        next_idx = max_idx + 1
    else:
        next_idx = 0

    print(f"\n=== inregistrare {n_samples} mostre pentru '{label}' ===")
    if label == "tello":
        print("rosteste 'tello' clar dupa 'VORBESTE' (1.5s per mostra)")
    else:
        print("rosteste un cuvant/comanda DIFERIT de 'tello' dupa 'VORBESTE'")
    min_rms = 200
    print()

    duration = 1.5
    n_frames = int(SAMPLE_RATE * duration)
    buffer = deque(maxlen=n_frames)
    capturing = {"on": False}
    captured = {"data": None, "ready": False}

    def cb(indata, frames, time_info, status):
        if capturing["on"]:
            buffer.extend(indata[:, 0])
            if len(buffer) >= n_frames:
                captured["data"] = np.array(buffer, dtype=np.int16)
                captured["ready"] = True
                capturing["on"] = False

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=1024,
        callback=cb,
    )
    stream.start()
    try:
        i = 0
        while i < n_samples:
            flush_stdin()
            input(f"[{i+1}/{n_samples}] Enter pentru inregistrare...")
            for n in ["3", "2", "1"]:
                print(f"  {n}..", end=" ", flush=True)
                time.sleep(0.7)
            print("VORBESTE", flush=True)

            buffer.clear()
            captured["ready"] = False
            capturing["on"] = True
            t0 = time.time()
            while not captured["ready"]:
                if time.time() - t0 > duration + 2.0:
                    print("  [!] timeout - reincearca\n")
                    capturing["on"] = False
                    break
                time.sleep(0.02)
            if not captured["ready"]:
                continue

            audio = captured["data"]
            rms = np.sqrt(np.mean((audio.astype(np.float32))**2))

            if rms < min_rms:
                print(f"  [!] tacere (rms={rms:.0f}) - reincearca\n")
                continue

            path = os.path.join(out_dir, f"{next_idx+i:03d}.wav")
            wavfile.write(path, SAMPLE_RATE, audio)
            print(f"  -> {os.path.basename(path)} (rms={rms:.0f})\n")
            i += 1
    finally:
        stream.stop()
        stream.close()

    print(f"gata: {n_samples} mostre salvate in {out_dir}")


def main():
    if len(sys.argv) < 3:
        print("uz: python -m tello.wakeword.record <label> <n>")
        print("ex: python -m tello.wakeword.record tello 20")
        print("ex: python -m tello.wakeword.record negative 20")
        sys.exit(1)
    record_session(sys.argv[1], int(sys.argv[2]))


if __name__ == "__main__":
    main()
