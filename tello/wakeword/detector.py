"""detector wake word: sliding window peste mic, prob > prag => trigger"""

import os
import pickle
import time
from collections import deque

import numpy as np
import sounddevice as sd

from tello.wakeword.features import extract_features, SAMPLE_RATE, CLIP_DURATION


MODEL_PATH = "data/wakeword_model.pkl"


class WakeWordDetector:
    def __init__(self, threshold=0.97, cooldown_s=2.0, model_path=MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"model lipsa: {model_path}\n"
                "ruleaza: python -m tello.wakeword.record tello 20\n"
                "         python -m tello.wakeword.record negative 20\n"
                "         python -m tello.wakeword.train"
            )
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)
        self.threshold = threshold
        self.cooldown_s = cooldown_s
        self.window_size = int(SAMPLE_RATE * CLIP_DURATION)
        self.hop_size = int(SAMPLE_RATE * 0.1)  # 100ms
        self.buffer = deque(maxlen=self.window_size)
        self._last_trigger = 0.0

    def predict_prob(self, audio_window):
        feat = extract_features(np.array(audio_window)).reshape(1, -1)
        return float(self.model.predict_proba(feat)[0, 1])

    def listen(self, on_detect, verbose=False):
        """blocheaza si apeleaza on_detect(prob) la fiecare detectie"""
        def stream_cb(indata, frames, time_info, status):
            self.buffer.extend(indata[:, 0])

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=self.hop_size,
            callback=stream_cb,
        ):
            print(f"ascult wake word (prag={self.threshold})...")
            while True:
                if len(self.buffer) < self.window_size:
                    time.sleep(0.05)
                    continue

                prob = self.predict_prob(self.buffer)
                if verbose and prob > 0.3:
                    print(f"  prob={prob:.2f}")

                now = time.time()
                if prob > self.threshold and (now - self._last_trigger) > self.cooldown_s:
                    self._last_trigger = now
                    on_detect(prob)

                time.sleep(self.hop_size / SAMPLE_RATE)

    def wait_for_trigger(self, verbose=False):
        """blocheaza pana la o detectie, apoi returneaza prob.
        Inchide stream-ul ca microfonul sa fie liber pentru recording."""
        def stream_cb(indata, frames, time_info, status):
            self.buffer.extend(indata[:, 0])

        self.buffer.clear()
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=self.hop_size,
            callback=stream_cb,
        ):
            while True:
                if len(self.buffer) < self.window_size:
                    time.sleep(0.05)
                    continue
                prob = self.predict_prob(self.buffer)
                if verbose and prob > 0.3:
                    print(f"  prob={prob:.2f}")
                now = time.time()
                if prob > self.threshold and (now - self._last_trigger) > self.cooldown_s:
                    self._last_trigger = now
                    return prob
                time.sleep(self.hop_size / SAMPLE_RATE)


def main():
    """test standalone: afiseaza la fiecare detectie"""
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    detector = WakeWordDetector()

    def on_detect(prob):
        print(f"\a[!] TELLO detectat! (prob={prob:.2f})")

    try:
        detector.listen(on_detect, verbose=verbose)
    except KeyboardInterrupt:
        print("\npa")


if __name__ == "__main__":
    main()
