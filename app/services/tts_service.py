from TTS.api import TTS
import os

class XTTSService:
    def __init__(self):
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        self.speaker_wav = "/Users/macuser/nova-audio/nova-reference.wav"
        self.output_path = "/Users/macuser/nova-audio/nova-response.wav"

    def synthesize(self, text: str) -> str:
        self.tts.tts_to_file(
            text=text,
            speaker_wav=self.speaker_wav,
            file_path=self.output_path,
            language="es"
        )
        return self.output_path