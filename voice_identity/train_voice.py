from pathlib import Path
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

BASE_DIR = Path(__file__).resolve().parent
PROFILE_PATH = BASE_DIR / "voice_profile.npy"
SAMPLE_PATH = BASE_DIR / "nahum_voice.wav"


def main() -> None:
    if not SAMPLE_PATH.exists():
        raise FileNotFoundError(f"No encontré el audio base en: {SAMPLE_PATH}")

    encoder = VoiceEncoder()
    wav = preprocess_wav(str(SAMPLE_PATH))
    embedding = encoder.embed_utterance(wav)

    np.save(PROFILE_PATH, embedding)
    print(f"Perfil guardado en: {PROFILE_PATH}")


if __name__ == "__main__":
    main()