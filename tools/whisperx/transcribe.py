#!/usr/bin/env python3
"""
Whisper transcription script for meeting recordings.
"""

import whisper
import json
import os
from pathlib import Path

# Config
AUDIO_DIR = "/Users/iiwabook/VSCode/tools/whisperx/audio"
OUTPUT_DIR = "/Users/iiwabook/VSCode/brain/00_Inbox"
MODEL_SIZE = "medium"  # tiny / base / small / medium / large
LANGUAGE = "ja"

# 残り4ファイル（1ファイル目は処理済み）
TARGET_FILES = [
    "2026-03-30-13-27-35.WAV",
    "2026-03-30-13-56-41.WAV",
    "2026-03-30-14-26-42.WAV",
    "2026-03-30-14-56-44.WAV",
]

def main():
    print(f"Loading Whisper model ({MODEL_SIZE})...", flush=True)
    model = whisper.load_model(MODEL_SIZE)
    print("Model loaded.\n", flush=True)

    for i, fname in enumerate(TARGET_FILES):
        audio_path = Path(AUDIO_DIR) / fname
        if not audio_path.exists():
            print(f"[{i+1}/{len(TARGET_FILES)}] SKIP (not found): {fname}", flush=True)
            continue

        # 既に処理済みならスキップ
        txt_path = Path(OUTPUT_DIR) / f"_transcribe_{audio_path.stem}.txt"
        if txt_path.exists():
            print(f"[{i+1}/{len(TARGET_FILES)}] SKIP (already done): {fname}", flush=True)
            continue

        print(f"[{i+1}/{len(TARGET_FILES)}] Transcribing: {fname}", flush=True)
        result = model.transcribe(str(audio_path), language=LANGUAGE, verbose=True)

        json_path = Path(OUTPUT_DIR) / f"_transcribe_{audio_path.stem}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

        print(f"  -> {len(result['segments'])} segments saved.", flush=True)

    print("\nAll done!", flush=True)

if __name__ == "__main__":
    main()
