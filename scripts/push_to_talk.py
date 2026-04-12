from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import httpx


API_URL = "http://127.0.0.1:8000/voice/respond-with-audio"
AUDIO_DIR = Path("/Users/macuser/nova-audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def record_audio() -> str:
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".m4a", dir=AUDIO_DIR).name

    print("\nPresiona ENTER para empezar a grabar...")
    input()

    print("Grabando... presiona ENTER para detener.")

    audio_device_index = "1"  # MacBook Pro Microphone

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "avfoundation",
        "-i", f":{audio_device_index}",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "aac",
        output_path,
    ]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    input()
    if process.stdin:
        process.stdin.write("q\n")
        process.stdin.flush()

    process.wait()
    print(f"Audio guardado en: {output_path}")
    return output_path


def send_audio(audio_path: str, conversation_id: str = "nova-ptt-1") -> dict:
    with open(audio_path, "rb") as f:
        files = {"file": (Path(audio_path).name, f, "audio/mp4")}
        data = {
            "language": "es",
            "conversation_id": conversation_id,
            "use_memory": "true",
        }

        response = httpx.post(API_URL, files=files, data=data, timeout=300.0)
        response.raise_for_status()
        return response.json()


def main() -> int:
    print("=== NOVA Push-to-Talk ===")
    print("Habla después de iniciar grabación. NOVA responderá al terminar.\n")

    while True:
        try:
            audio_path = record_audio()
            result = send_audio(audio_path)

            print("\n--- TRANSCRIPT ---")
            print(result.get("transcript", ""))

            print("\n--- INTENT ---")
            print(result.get("intent", ""))

            print("\n--- RESPONSE ---")
            print(result.get("response", ""))

            print("\n--- AUDIO PATH ---")
            print(result.get("audio_path", ""))

            again = input("\n¿Quieres hablar otra vez? (y/n): ").strip().lower()
            if again not in {"y", "yes", "s", "si"}:
                print("Cerrando NOVA push-to-talk.")
                break

        except KeyboardInterrupt:
            print("\nInterrumpido por usuario.")
            break
        except Exception as exc:
            print(f"\nError: {exc}")
            break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())