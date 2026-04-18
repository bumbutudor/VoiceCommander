"""extragere features audio pentru wake word"""

import numpy as np
import librosa


SAMPLE_RATE = 16000
CLIP_DURATION = 1.0  # secunde
N_MFCC = 13


def extract_features(audio, sr=SAMPLE_RATE):
    """audio (1d array, float sau int16) -> vector feature fix de 78 valori"""
    audio = audio.astype(np.float32)
    if np.abs(audio).max() > 1.5:
        audio = audio / 32768.0

    target_len = int(sr * CLIP_DURATION)
    if len(audio) < target_len:
        audio = np.pad(audio, (0, target_len - len(audio)))
    else:
        audio = audio[:target_len]

    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=N_MFCC)
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)

    feats = np.concatenate([mfcc, delta, delta2], axis=0)  # (39, T)
    # mean+std pooling pe axa timp -> (78,)
    return np.concatenate([feats.mean(axis=1), feats.std(axis=1)])


def augment(audio, sr=SAMPLE_RATE, n=8):
    """genereaza n variante augmentate (noise/shift/volum/pitch)"""
    audio = audio.astype(np.float32)
    if np.abs(audio).max() > 1.5:
        audio = audio / 32768.0

    out = [audio]
    for _ in range(n):
        a = audio.copy()
        # gaussian noise
        if np.random.rand() < 0.7:
            noise = np.random.randn(len(a)) * 0.005 * np.random.rand()
            a = a + noise
        # time shift +-100ms
        if np.random.rand() < 0.7:
            shift = np.random.randint(-int(sr * 0.1), int(sr * 0.1))
            a = np.roll(a, shift)
        # scalare volum
        if np.random.rand() < 0.7:
            a = a * (0.5 + np.random.rand())
        # pitch shift +-2 semitone
        if np.random.rand() < 0.4:
            try:
                steps = (np.random.rand() - 0.5) * 4
                a = librosa.effects.pitch_shift(a, sr=sr, n_steps=steps)
            except Exception:
                pass
        out.append(a.astype(np.float32))
    return out
