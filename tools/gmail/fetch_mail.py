#!/usr/bin/env python3
"""
Gmail メール取得ツール（IMAP接続）

使い方:
  python fetch_mail.py --query "退職"
  python fetch_mail.py --query "健康保険 社会保険 離職票 年金" --max 30 --save
  python fetch_mail.py --inbox --max 20
"""

import argparse
import imaplib
import email
import re
from email.header import decode_header
from pathlib import Path
from datetime import datetime


TOOLS_DIR = Path(__file__).parent


def load_env() -> dict:
    env = {}
    env_path = TOOLS_DIR / ".env"
    if not env_path.exists():
        raise FileNotFoundError(f".env が見つかりません: {env_path}")
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def decode_str(s) -> str:
    if s is None:
        return ""
    parts = decode_header(s)
    result = ""
    for part, enc in parts:
        if isinstance(part, bytes):
            result += part.decode(enc or "utf-8", errors="replace")
        else:
            result += part
    return result


def get_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(charset, errors="replace")
                    break
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(charset, errors="replace")
    return body[:500].replace("\n", " ").strip()


def connect(address: str, app_password: str) -> imaplib.IMAP4_SSL:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(address, app_password)
    return mail


def fetch_messages(mail, query_words: list, max_results: int = 20, inbox_only: bool = False) -> list:
    # [Gmail]/すべてのメール は modified UTF-7 エンコード名を使用
    mailbox = "INBOX" if inbox_only else '"[Gmail]/&MFkweTBmMG4w4TD8MOs-"'
    status, _ = mail.select(mailbox)
    if status != "OK":
        mail.select("INBOX")

    if inbox_only:
        _, data = mail.uid("SEARCH", "UNSEEN")
        ids = data[0].split()
    else:
        # 2026年以降のメールを全取得してローカルでキーワードフィルタ
        _, data = mail.uid("SEARCH", "SINCE", "01-Jan-2026")
        ids = data[0].split()

    if not ids:
        print(f"[fetch] 該当メールなし")
        return []

    # 新しい順に並び替え
    ids = ids[::-1]
    print(f"[fetch] {len(ids)}件を確認中（キーワードフィルタあり）...")

    mails = []
    for uid in ids:
        if len(mails) >= max_results:
            break
        _, msg_data = mail.uid("FETCH", uid, "(RFC822)")
        if not msg_data or not msg_data[0]:
            continue
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        subject = decode_str(msg.get("Subject", ""))
        body    = get_body(msg)

        # キーワードフィルタ（件名か本文にいずれか含む）
        if not inbox_only and query_words:
            combined = (subject + " " + body).lower()
            if not any(w.lower() in combined for w in query_words):
                continue

        mails.append({
            "date":    decode_str(msg.get("Date", "")),
            "from":    decode_str(msg.get("From", "")),
            "subject": subject,
            "body":    body,
        })
    return mails


def print_mails(mails: list):
    for i, m in enumerate(mails, 1):
        print(f"\n{'─'*60}")
        print(f"[{i}] {m['date']}")
        print(f"差出人: {m['from']}")
        print(f"件名:   {m['subject']}")
        print(f"本文:   {m['body'][:200]}")


def save_to_brain(mails: list, query: str) -> Path:
    out_dir = TOOLS_DIR.parent.parent / "brain" / "00_Inbox"
    out_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^\w]", "_", query)[:20]
    out_path = out_dir / f"{date_str}_gmail_{slug}.md"

    lines = [f"# Gmail取得：{query}\n> 取得日: {date_str}\n\n"]
    for i, m in enumerate(mails, 1):
        lines.append(f"## [{i}] {m['subject']}")
        lines.append(f"- **日付**: {m['date']}")
        lines.append(f"- **差出人**: {m['from']}")
        lines.append(f"- **本文抜粋**: {m['body'][:300]}\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[save] → {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="退職", help="検索キーワード（スペース区切りでOR検索）")
    parser.add_argument("--max",   type=int, default=20)
    parser.add_argument("--inbox", action="store_true", help="未読メール一覧")
    parser.add_argument("--save",  action="store_true", help="brain/00_Inbox に保存")
    args = parser.parse_args()

    env = load_env()
    address      = env["GMAIL_ADDRESS"]
    app_password = env["GMAIL_APP_PASSWORD"].replace(" ", "")

    print(f"[connect] {address} に接続中...")
    mail = connect(address, app_password)
    print("[connect] 接続成功")

    query_words = args.query.split()
    mails = fetch_messages(mail, query_words, args.max, args.inbox)
    mail.logout()

    if not mails:
        return

    print_mails(mails)

    if args.save:
        save_to_brain(mails, args.query)
    else:
        print(f"\n💡 --save を付けると brain/00_Inbox に保存されます")


if __name__ == "__main__":
    main()
