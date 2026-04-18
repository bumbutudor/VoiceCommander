"""backend-uri pluggable pentru transcriere whisper

interfata: clasa cu metoda transcribe(audio_int16_np_array) -> str
"""

import os
import subprocess
import tempfile

import numpy as np

from core import config


class FasterWhisperBackend:
    """faster-whisper - default pe PC x86_64"""

    def __init__(self):
        from faster_whisper import WhisperModel
        try:
            self.model = WhisperModel(
                config.WHISPER_MODEL,
                device="cpu",
                compute_type="int8",
                local_files_only=True,
            )
        except Exception:
            # nu e in cache - descarca (necesita internet)
            self.model = WhisperModel(
                config.WHISPER_MODEL,
                device="cpu",
                compute_type="int8",
            )

    def transcribe(self, audio):
        audio_f32 = audio.astype(np.float32).flatten() / 32768.0
        segments, _ = self.model.transcribe(
            audio_f32,
            language=config.WHISPER_LANGUAGE,
            vad_filter=True,
            beam_size=3,
        )
        return " ".join(s.text for s in segments).strip().lower()


class WhisperCppBackend:
    """whisper.cpp prin subprocess - pentru Termux/Android ARM

    cere:
      - binary `whisper-cli` (sau cel din WHISPER_CPP_BIN) in PATH
      - model ggml descarcat la WHISPER_CPP_MODEL
    """

    def __init__(self):
        self.bin = config.WHISPER_CPP_BIN
        self.model = config.WHISPER_CPP_MODEL
        if not os.path.exists(self.model):
            raise RuntimeError(
                f"model whisper.cpp lipseste: {self.model}\n"
                "ruleaza: bash ~/whisper.cpp/models/download-ggml-model.sh tiny"
            )

    def transcribe(self, audio):
        from scipy.io.wavfile import write as wav_write
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name
        try:
            wav_write(wav_path, 16000, audio.astype(np.int16).flatten())
            result = subprocess.run(
                [
                    self.bin,
                    "-m", self.model,
                    "-f", wav_path,
                    "-l", config.WHISPER_LANGUAGE,
                    "-nt",   # no timestamps
                    "-np",   # no progress
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.stdout.strip().lower()
        finally:
            try:
                os.unlink(wav_path)
            except OSError:
                pass


def make_backend():
    name = config.WHISPER_BACKEND.lower()
    if name == "cpp":
        return WhisperCppBackend()
    return FasterWhisperBackend()
