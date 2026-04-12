from __future__ import annotations

import subprocess
import tempfile
import time
from pathlib import Path

import httpx
import numpy as np
import sounddevice as sd
import soundfile as sf


API_URL = "http://127.0.0.1:8000/voice/respond-with-audio"
AUDIO_DIR = Path("/Users/macuser/nova-audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

CONVERSATION_ID = "terra-continuous-1"

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_DURATION = 0.2  # segundos
BLOCK_SIZE = int(SAMPLE_RATE * BLOCK_DURATION)

START_THRESHOLD = 0.008   # sensibilidad de inicio
SILENCE_THRESHOLD = 0.006 # sensibilidad de silencio
MAX_SILENCE_SECONDS = 0.8
MAX_RECORD_SECONDS = 10.0
MIN_SPEECH_SECONDS = 0.5


def rms(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio))))


def record_until_silence() -> str | None:
    print("\nEscuchando... habla cuando quieras.")

    frames: list[np.ndarray] = []
    speech_started = False
    silence_time = 0.0
    speech_time = 0.0
    total_time = 0.0

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        blocksize=BLOCK_SIZE,
    ) as stream:
        while total_time < MAX_RECORD_SECONDS:
            audio_chunk, _ = stream.read(BLOCK_SIZE)
            # reducir ruido bajo
            audio_chunk = np.where(np.abs(audio_chunk) < 0.005, 0, audio_chunk)
            level = rms(audio_chunk)
            print(f"Nivel audio: {level:.4f}")
            total_time += BLOCK_DURATION

            if not speech_started:
                if level >= START_THRESHOLD:
                    speech_started = True
                    frames.append(audio_chunk.copy())
                    speech_time += BLOCK_DURATION
            else:
                frames.append(audio_chunk.copy())

                if level >= SILENCE_THRESHOLD:
                    silence_time = 0.0
                    speech_time += BLOCK_DURATION
                else:
                    silence_time += BLOCK_DURATION

                if speech_time >= MIN_SPEECH_SECONDS and silence_time >= MAX_SILENCE_SECONDS:
                    break

    if not speech_started or not frames:
        return None

    audio = np.concatenate(frames, axis=0)
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=AUDIO_DIR).name
    sf.write(output_path, audio, SAMPLE_RATE)
    print(f"Audio capturado en: {output_path}")
    return output_path


def send_audio(audio_path: str) -> dict:
    with open(audio_path, "rb") as f:
        files = {"file": (Path(audio_path).name, f, "audio/wav")}
        data = {
            "language": "es",
            "conversation_id": CONVERSATION_ID,
            "use_memory": "true",
            "autoplay": "false",
        }

        response = httpx.post(API_URL, files=files, data=data, timeout=300.0)

        if response.status_code >= 400:
            print("\n--- ERROR BODY ---")
            print(response.text)
            response.raise_for_status()

        return response.json()
    
def play_audio(audio_path: str) -> None:
    if not audio_path:
        return

    subprocess.run(
        ["afplay", "-q", "1", audio_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def main() -> int:
    print("=== TERRA Continuous Voice ===")
    print("Habla. TERRA detectará tu voz, cortará en silencio y responderá automáticamente.")
    print("Presiona Ctrl+C para salir.\n")

    while True:
        try:
            audio_path = record_until_silence()

            if not audio_path:
                print("No detecté voz útil. Sigo escuchando...")
                time.sleep(0.3)
                continue

            result = send_audio(audio_path)

            transcript = result.get("transcript", "").strip()
            intent = result.get("intent", "")
            response = result.get("response", "")
            audio_path_out = result.get("audio_path", "")
            tts_error = result.get("tts_error")
            spoken_response = result.get("spoken_response", "")

            if transcript:
                print("\n--- TRANSCRIPT ---")
                print(transcript)

                print("\n--- INTENT ---")
                print(intent)

                print("\n--- RESPONSE ---")
                print(response)

                print("\n--- AUDIO PATH ---")
                print(audio_path_out)


                if audio_path_out:
                    print("\nTERRA está respondiendo...")
                    play_audio(audio_path_out)
                    time.sleep(0.5)
                
                print("\n--- SPOKEN RESPONSE ---")
                print(spoken_response)

            else:
                print("\nNo se detectó voz útil en este ciclo.")

            if tts_error:
                print(f"\n--- TTS ERROR ---")
                print(tts_error)

            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\nTERRA continuous voice cerrado.")
            break
        except Exception as exc:
            print(f"\nError: {exc}")
            time.sleep(1.0)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())