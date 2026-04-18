"""antreneaza clasificator wake word din mostre inregistrate"""

import os
import glob
import pickle

import numpy as np
from scipy.io import wavfile
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

from tello.wakeword.features import extract_features, augment


DATA_DIR = "data/wakeword"
MODEL_PATH = "data/wakeword_model.pkl"


def load_data():
    X, y = [], []
    if not os.path.isdir(DATA_DIR):
        raise SystemExit(f"nu exista {DATA_DIR} - ruleaza intai record")

    for label in os.listdir(DATA_DIR):
        full = os.path.join(DATA_DIR, label)
        if not os.path.isdir(full):
            continue
        is_pos = (label == "tello")
        wavs = glob.glob(os.path.join(full, "*.wav"))
        print(f"  {label}: {len(wavs)} mostre")

        for w in wavs:
            sr, audio = wavfile.read(w)
            n_aug = 10 if is_pos else 3
            for variant in augment(audio, sr=sr, n=n_aug):
                X.append(extract_features(variant, sr=sr))
                y.append(1 if is_pos else 0)

    return np.array(X), np.array(y)


def main():
    print("incarcare date...")
    X, y = load_data()
    n_pos = int(y.sum())
    print(f"\ntotal: {len(X)} samples ({n_pos} pozitive, {len(y)-n_pos} negative)")

    if n_pos < 5 or len(y) - n_pos < 5:
        raise SystemExit("nu sunt suficiente mostre, ai nevoie de cel putin 5 din fiecare clasa")

    print("\nantrenare logistic regression...")
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=2000, C=1.0)),
    ])

    # cross-val pentru estimare reala
    scores = cross_val_score(model, X, y, cv=5)
    print(f"acuratete cv: {scores.mean():.3f} (+- {scores.std():.3f})")

    model.fit(X, y)
    print(f"acuratete training: {model.score(X, y):.3f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"\nmodel salvat: {MODEL_PATH}")


if __name__ == "__main__":
    main()
