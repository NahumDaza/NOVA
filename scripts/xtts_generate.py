from __future__ import annotations

import os
import sys

from TTS.api import TTS


def main() -> int:
    if len(sys.argv) < 3:
        print("Uso: python xtts_generate.py <texto> <output_path>")
        return 1

    text = sys.argv[1]
    output_path = sys.argv[2]

    os.environ["COQUI_TOS_AGREED"] = "1"

    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    tts.tts_to_file(
        text=text,
        speaker_wav="/Users/macuser/nova-audio/nova-reference.wav",
        file_path=output_path,
        language="es",
    )

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())