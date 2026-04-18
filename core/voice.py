"""captura audio de la microfon si transcriere cu faster-whisper"""

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from core import config


class Listener:
    def __init__(self):
        # local_files_only: nu incearca sa contacteze HF (blocheaza fara internet,
        # ex: cand esti conectat pe wifi-ul dronei tello)
        try:
            self.model = WhisperModel(
                config.WHISPER_MODEL,
                device="cpu",
                compute_type="int8",
                local_files_only=True,
            )
        except Exception:
            # daca modelul nu e in cache, descarca-l (necesita internet)
            self.model = WhisperModel(
                config.WHISPER_MODEL,
                device="cpu",
                compute_type="int8",
            )

        self.rate = 16000
        self.chunk_ms = 100
        self.chunk_size = int(self.rate * self.chunk_ms / 1000)
        self.silence_limit_s = 1.5
        self.min_speech_s = 0.3
        self.max_speech_s = 15.0
        self.threshold = None

    def calibrate(self):
        """calibreaza pragul de zgomot ambiental"""
        print("calibrare microfon (liniste 2s)...")
        audio = sd.rec(
            int(self.rate * 2),
            samplerate=self.rate,
            channels=1,
            dtype="int16",
        )
        sd.wait()
        noise = np.abs(audio).mean()
        self.threshold = max(noise * 3, 150)
        print(f"prag zgomot: {self.threshold:.0f}")

    def record(self):
        """asteapta vorbire, inregistreaza pana la liniste"""
        if self.threshold is None:
            self.calibrate()

        max_silence = int(self.silence_limit_s * 1000 / self.chunk_ms)
        max_chunks = int(self.max_speech_s * 1000 / self.chunk_ms)
        min_chunks = int(self.min_speech_s * 1000 / self.chunk_ms)

        frames = []
        speaking = False
        silence = 0

        stream = sd.InputStream(
            samplerate=self.rate,
            channels=1,
            dtype="int16",
            blocksize=self.chunk_size,
        )
        stream.start()

        try:
            total = 0
            while total < max_chunks + max_silence + 500:
                data, _ = stream.read(self.chunk_size)
                energy = np.abs(data).mean()
                total += 1

                if energy > self.threshold:
                    speaking = True
                    silence = 0
                    frames.append(data.copy())
                elif speaking:
                    frames.append(data.copy())
                    silence += 1
                    if silence >= max_silence:
                        break
        finally:
            stream.stop()
            stream.close()

        if len(frames) < min_chunks:
            return None

        return np.concatenate(frames)

    def transcribe(self, audio):
        """transcriere audio -> text cu whisper"""
        audio_f32 = audio.astype(np.float32).flatten() / 32768.0
        segments, _ = self.model.transcribe(
            audio_f32,
            language=config.WHISPER_LANGUAGE,
            vad_filter=True,
            beam_size=3,
        )
        return " ".join(s.text for s in segments).strip().lower()

    def listen(self):
        """asculta si returneaza textul transcris"""
        audio = self.record()
        if audio is None:
            return ""
        return self.transcribe(audio)
