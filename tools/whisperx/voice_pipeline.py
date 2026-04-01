#!/usr/bin/env python3
"""
音声文字起こしパイプライン

フロー:
  1. レコーダー(NO NAME)からローカルにWAVをコピー（--sync）
  2. MLX Whisperでローカルの未処理WAVを文字起こし → brain/3_LOGS/transcripts/raw/ に保存
  3. 処理済みWAVをGoogle Drive voice_archive/ に移動

  日次処理（--daily）:
  4. transcripts/raw/ から1日分の.txtを結合してGeminiで場面識別
  5. 場面ごとにファイルを結合して詳細ファイルを生成（全場面）
     例: 2026-03-30_03_detail_1_熊野町役場会議.md
  6. raw/ の30日経過ファイルを自動削除
  7. --upload で指定場面をKumano AI Studio Driveへ転送

使い方:
  python voice_pipeline.py                         # 未処理WAVを全部処理
  python voice_pipeline.py --sync                  # レコーダーからコピーして処理
  python voice_pipeline.py --daily 2026-03-30      # 場面識別＋議事録生成
  python voice_pipeline.py --upload 2026-03-30     # 全場面をKumano Driveへ転送
  python voice_pipeline.py --upload 2026-03-30 1   # scene1だけKumano Driveへ転送
"""

import os
import re
import shutil
import sys
from pathlib import Path

# ─── パス設定 ─────────────────────────────────────────────
REPO_ROOT      = Path(__file__).parent.parent.parent
AUDIO_DIR      = REPO_ROOT / "brain" / "0_RAW" / "audio"
TRANSCRIPT_DIR = REPO_ROOT / "brain" / "3_LOGS" / "transcripts"
RAW_DIR        = TRANSCRIPT_DIR / "raw"   # 全rawテキスト（30日保持後自動削除）

GDRIVE_PERSONAL = Path.home() / "Library" / "CloudStorage" / \
                  "GoogleDrive-t.iwaiwawaiwai@gmail.com" / "マイドライブ"
ARCHIVE_DIR     = GDRIVE_PERSONAL / "voice_archive"

GDRIVE_KUMANO   = Path.home() / "Library" / "CloudStorage" / \
                  "GoogleDrive-iwamasa.t@kumano-ai-studio.com" / "マイドライブ"
MINUTES_DIR     = GDRIVE_KUMANO / "minutes"

MLX_MODEL    = "mlx-community/whisper-large-v3-turbo"
GEMINI_MODEL = "gemini-2.5-flash"

# ─── プロンプト ────────────────────────────────────────────
SCENE_DETECT_PROMPT = """\
以下は1日分の音声録音を30分ごとに文字起こしした内容です。
ノイズ文字（재 재 재 など韓国語文字の繰り返し）は無視してください。
「=== YYYY-MM-DD-HH-MM-SS ===」はファイルの開始時刻です。

## タスク: 場面識別

**場面の区切り方（重要）:**
- 場面は「場所」「参加者」「目的」が変わったときに切り替わります
- 同じ場所・同じメンバーで話題が変わっても、それは同一場面です
- 例: 役場での会議は話題が複数あっても1つの場面、その後マクドナルドに移動したら別の場面

場面タイプ:
- **formal_meeting**: 複数人が参加する正式な打ち合わせ・会議
- **informal_chat**: 移動中・廊下など、その場かぎりの立ち話・雑談
- **internal_review**: 少人数（2〜3人）での振り返り・内部検討

各場面に `files` として、その場面に含まれるファイル名（拡張子なし）のリストを含めてください。

以下のJSON形式のみで出力してください：

```json
{{
  "scenes": [
    {{
      "type": "formal_meeting",
      "title": "場面のタイトル（簡潔に）",
      "files": ["2026-03-30-11-57-30", "2026-03-30-12-27-31", "2026-03-30-12-57-32"],
      "tags": ["熊野AIスタジオ", "公共交通"],
      "summary": "3〜5行の概要",
      "location": "場所（推定でよい。不明なら null）",
      "participants": ["参加者名1", "参加者名2"],
      "start_time": "HH:MM（最初のファイル名から推定。不明なら null）",
      "end_time": "HH:MM（最後のファイル名から推定。不明なら null）"
    }}
  ]
}}
```

---
{combined}
"""

MINUTES_PROMPT = """\
以下は会議・打ち合わせの音声文字起こしです（複数の30分録音を結合したものです）。
ノイズ文字（재 재 재 など）は無視してください。

以下の議事録フォーマットで出力してください：

## 概要
（3〜5行）

## 議題・主なトピック
（箇条書き）

## 決定事項・アクションアイテム
（誰が・何を。不明な場合は「要確認」）

## メモ・気づき
（重要な固有名詞、背景情報など）

---
{combined}
"""


# ─── 1. レコーダー同期 ────────────────────────────────────
def sync_recorder():
    sys.path.insert(0, str(Path(__file__).parent))
    from sync_recorder import sync_recorder as _sync
    return _sync()


# ─── 2. 文字起こし ────────────────────────────────────────
def transcribe(wav_path: Path) -> str:
    import mlx_whisper
    print(f"[transcribe] {wav_path.name} ...")
    result = mlx_whisper.transcribe(
        str(wav_path),
        path_or_hf_repo=MLX_MODEL,
        language="ja",
        condition_on_previous_text=False,
        no_speech_threshold=0.6,
        compression_ratio_threshold=2.4,
    )
    text = result["text"].strip()
    print(f"[transcribe] 完了 ({len(text)} 文字)")
    return text


# ─── 3. テキスト保存 ──────────────────────────────────────
def save_transcript(wav_path: Path, transcript: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / wav_path.with_suffix(".txt").name
    out_path.write_text(transcript, encoding="utf-8")
    print(f"[save] {out_path.relative_to(REPO_ROOT)}")
    return out_path


# ─── 4. WAVをアーカイブ ───────────────────────────────────
def archive_wav(wav_path: Path):
    date = wav_path.stem[:10]
    dest_dir = ARCHIVE_DIR / date
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(wav_path), str(dest_dir / wav_path.name))
    print(f"[archive] {wav_path.name} → GDrive/voice_archive/{date}/")


# ─── 5. 日次処理（場面識別＋場面別議事録） ───────────────
def _slugify(title: str) -> str:
    """タイトルをファイル名用に変換"""
    title = re.sub(r'[\\/:*?"<>|]', '', title)
    return title.replace(' ', '_')[:30]


def daily_process(date_str: str) -> None:
    import json
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[daily] GEMINI_API_KEY が未設定のためスキップ")
        return

    month = date_str[:7]
    out_dir = TRANSCRIPT_DIR / month / date_str   # 出力先サブフォルダ
    out_dir.mkdir(parents=True, exist_ok=True)

    # 共通 raw/ フォルダから検索
    txts = sorted(RAW_DIR.glob(f"{date_str}*.txt"))
    if not txts:
        print(f"[daily] テキストが見つかりません: {date_str}")
        return

    # ── Step1: 全テキスト結合して場面識別 ──
    combined = ""
    txt_map = {}
    for txt in txts:
        combined += f"\n\n=== {txt.stem} ===\n" + txt.read_text(encoding="utf-8")
        txt_map[txt.stem] = txt

    print(f"[daily] {date_str} ({len(txts)}ファイル, {len(combined):,}文字) 場面識別中 ...")

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=SCENE_DETECT_PROMPT.format(combined=combined)
        )
        raw = (resp.text or "").strip()
        if not raw:
            print(f"[daily] Geminiのレスポンスが空です。リトライしてください。")
            return

        json_match = re.search(r"```json\s*(.*?)\s*```", raw, re.DOTALL)
        data = json.loads(json_match.group(1) if json_match else raw)
        scenes = data.get("scenes", [])
        print(f"[daily] {len(scenes)}場面を識別")

        # ── Step2: 01_summary.md（場面インデックス） ──
        type_icon  = {"formal_meeting": "🏛", "informal_chat": "💬", "internal_review": "🔍"}
        type_label = {"formal_meeting": "正式会議", "informal_chat": "立ち話", "internal_review": "内部検討"}
        index_lines = [f"# {date_str} サマリー\n"]
        for i, scene in enumerate(scenes, 1):
            icon     = type_icon.get(scene.get("type", ""), "📄")
            title    = scene.get("title", f"scene{i}")
            tags_str = " | ".join(scene.get("tags", []))
            index_lines.append(f"## {icon} {i}. {title}")
            index_lines.append(f"**種別：** {type_label.get(scene.get('type',''), '')}　**タグ：** {tags_str}\n")
            index_lines.append(f"{scene.get('summary', '')}\n")

        summary_path = out_dir / f"{date_str}_01_summary.md"
        summary_path.write_text("\n".join(index_lines), encoding="utf-8")
        print(f"[01] → {summary_path.relative_to(REPO_ROOT)}")

        # ── Step3: 場面ごとに 03_detail_N_ を生成（全場面） ──
        meeting_scenes = []
        detail_num = 1
        for i, scene in enumerate(scenes, 1):
            scene_type = scene.get("type", "")
            title      = scene.get("title", f"scene{i}")
            files      = scene.get("files", [])
            tags       = scene.get("tags", [])

            scene_txts = [txt_map[f] for f in files if f in txt_map]
            if not scene_txts:
                print(f"[{i}] 対応ファイルなし: {title}")
                continue

            scene_combined = ""
            for t in scene_txts:
                scene_combined += f"\n\n=== {t.stem} ===\n" + t.read_text(encoding="utf-8")

            print(f"[03-{detail_num}] 詳細生成中: {title} ({len(scene_txts)}ファイル)")

            resp = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=MINUTES_PROMPT.format(combined=scene_combined)
            )
            detail_raw = (resp.text or "（生成できませんでした）").strip()

            slug     = _slugify(title)
            filename = f"{date_str}_03_detail_{detail_num}_{slug}.md"
            tags_str = " | ".join(tags)

            # 会議系は「議事録：」、立ち話は「記録：」
            heading = "議事録" if scene_type in ("formal_meeting", "internal_review") else "記録"
            location     = scene.get("location") or "不明"
            participants = "、".join(scene.get("participants") or []) or "不明"
            start_time   = scene.get("start_time")
            end_time     = scene.get("end_time")
            time_str     = f"{date_str} {start_time}〜{end_time}" if start_time else date_str
            content = (
                f"# {heading}：{title}\n\n"
                f"**日時：** {time_str}\n"
                f"**場所：** {location}\n"
                f"**参加者：** {participants}\n"
                f"**種別：** {type_label.get(scene_type, scene_type)}\n"
                f"**タグ：** {tags_str}\n\n"
                f"---\n\n{detail_raw}\n"
            )
            out_path = out_dir / filename
            out_path.write_text(content, encoding="utf-8")
            print(f"[03-{detail_num}] → {out_path.relative_to(REPO_ROOT)}")

            # 統合議事録（02）は会議系のみ
            if scene_type in ("formal_meeting", "internal_review"):
                meeting_scenes.append({"num": detail_num, "title": title, "tags": tags, "content": detail_raw})
            detail_num += 1

        # ── Step4: 02_minutes.md（全正式会議の統合） ──
        if meeting_scenes:
            print(f"[02] 統合議事録生成中 ...")
            all_combined = "\n\n".join(
                f"## {'=' * 40}\n## 場面{s['num']}: {s['title']}\n\n{s['content']}"
                for s in meeting_scenes
            )
            minutes_path = out_dir / f"{date_str}_02_minutes.md"
            minutes_path.write_text(
                f"# {date_str} 議事録（統合）\n\n{all_combined}\n",
                encoding="utf-8"
            )
            print(f"[02] → {minutes_path.relative_to(REPO_ROOT)}")

        # ── Step5: 30日経過した raw txt を自動削除 ──
        cleanup_raw(days=30)

        print(f"\nKumano Driveに上げる場合:")
        print(f"  全場面: python voice_pipeline.py --upload {date_str}")
        for s in meeting_scenes:
            print(f"  {s['num']}のみ: python voice_pipeline.py --upload {date_str} {s['num']}")

    except Exception as e:
        import traceback
        print(f"[daily] エラー: {e}")
        traceback.print_exc()


# ─── 6. raw txt クリーンアップ（30日保持） ───────────────
def cleanup_raw(days: int = 30) -> None:
    from datetime import datetime, timedelta
    if not RAW_DIR.exists():
        return
    cutoff = datetime.now() - timedelta(days=days)
    deleted = [
        f for f in RAW_DIR.glob("*.txt")
        if datetime.fromtimestamp(f.stat().st_mtime) < cutoff
        and not f.unlink()  # unlink() returns None → falsy → keeps f in list
    ]
    if deleted:
        print(f"[cleanup] {len(deleted)}件を削除（{days}日以上経過）")


# ─── 7. Kumano Drive へアップロード ──────────────────────
def upload_to_kumano(date_str: str, scene_num: str = None) -> None:
    month = date_str[:7]
    local_dir  = TRANSCRIPT_DIR / month / date_str
    kumano_dir = MINUTES_DIR / month / date_str
    kumano_dir.mkdir(parents=True, exist_ok=True)

    if scene_num:
        pattern = f"{date_str}_03_detail_{scene_num}_*.md"
    else:
        pattern = f"{date_str}_*.md"

    files = sorted(local_dir.glob(pattern))
    if not files:
        print(f"[upload] 対象ファイルなし: {pattern}")
        print(f"  先に: python voice_pipeline.py --daily {date_str}")
        return

    for f in files:
        shutil.copy2(str(f), str(kumano_dir / f.name))
        print(f"[upload] {f.name} → Kumano Drive/minutes/{month}/")

    print(f"[upload] 完了（{len(files)}ファイル）")


# ─── メイン ───────────────────────────────────────────────
def process_file(wav_path: Path):
    transcript = transcribe(wav_path)
    if not transcript:
        print(f"[warn] 空: {wav_path.name}")
        return
    save_transcript(wav_path, transcript)
    archive_wav(wav_path)
    print(f"[done] {wav_path.name} 完了\n")


def main():
    args = sys.argv[1:]

    if "--upload" in args:
        idx = args.index("--upload")
        date_str   = args[idx + 1] if idx + 1 < len(args) else None
        scene_num  = args[idx + 2] if idx + 2 < len(args) and not args[idx + 2].startswith("--") else None
        if not date_str:
            print("使い方: python voice_pipeline.py --upload 2026-03-30 [scene番号]")
            return
        upload_to_kumano(date_str, scene_num)
        return

    if "--daily" in args:
        idx = args.index("--daily")
        date_str = args[idx + 1] if idx + 1 < len(args) else None
        if not date_str:
            print("使い方: python voice_pipeline.py --daily 2026-03-30")
            return
        daily_process(date_str)
        return

    if "--sync" in args:
        args.remove("--sync")
        print("=== レコーダー同期 ===")
        sync_recorder()

    targets = [Path(a) for a in args] if args else []
    if not targets:
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        targets = [w for w in
                   sorted(AUDIO_DIR.glob("*.WAV")) + sorted(AUDIO_DIR.glob("*.wav"))
                   if w.is_file()]

    if not targets:
        print(f"処理対象の WAV が見つかりません: {AUDIO_DIR}")
        return

    print(f"=== 処理対象: {len(targets)} ファイル ===")
    for wav in targets:
        process_file(wav)
    print("=== 完了 ===")
    print("次: python voice_pipeline.py --daily YYYY-MM-DD  で議事録を生成")


if __name__ == "__main__":
    main()
