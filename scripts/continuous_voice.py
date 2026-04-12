from __future__ import annotations

import subprocess
import tempfile
import time
from pathlib import Path

import httpx


API_URL = "http://127.0.0.1:8000/voice/respond-with-audio"
AUDIO_DIR = Path("/Users/macuser/nova-audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_DEVICE_INDEX = "1"  # MacBook Pro Microphone
CONVERSATION_ID = "terra-continuous-1"


def record_until_silence() -> str:
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".m4a", dir=AUDIO_DIR).name

    print("\nEscuchando... habla cuando quieras.")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "avfoundation",
        "-i", f":{AUDIO_DEVICE_INDEX}",
        "-af", "silenceremove=stop_periods=1:stop_duration=1.2:stop_threshold=-45dB",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "aac",
        output_path,
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    print(f"Audio capturado en: {output_path}")
    return output_path


def send_audio(audio_path: str) -> dict:
    with open(audio_path, "rb") as f:
        files = {"file": (Path(audio_path).name, f, "audio/mp4")}
        data = {
            "language": "es",
            "conversation_id": CONVERSATION_ID,
            "use_memory": "true",
        }

        response = httpx.post(API_URL, files=files, data=data, timeout=300.0)
        response.raise_for_status()
        return response.json()


def main() -> int:
    print("=== TERRA Continuous Voice ===")
    print("Habla. TERRA escuchará, procesará y responderá.")
    print("Presiona Ctrl+C para salir.\n")

    while True:
        try:
            audio_path = record_until_silence()

            result = send_audio(audio_path)

            print("\n--- TRANSCRIPT ---")
            print(result.get("transcript", ""))

            print("\n--- INTENT ---")
            print(result.get("intent", ""))

            print("\n--- RESPONSE ---")
            print(result.get("response", ""))

            print("\n--- AUDIO PATH ---")
            print(result.get("audio_path", ""))

            time.sleep(0.6)

        except KeyboardInterrupt:
            print("\nTERRA continuous voice cerrado.")
            break
        except Exception as exc:
            print(f"\nError: {exc}")
            time.sleep(1.5)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())