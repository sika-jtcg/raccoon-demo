#!/usr/bin/env python3
"""公開前チェック：data.json に注文番号・工單／会話 ID・個人情報が含まれていないか検査する。
使い方: python3 check_pii.py data.json   （NG なら exit 1）"""
import json, re, sys

BANNED_KEYS = {"order_id", "order_number", "external_order_id", "ticket_id", "conversation_id",
               "tracking_id", "trace_id", "bot_id", "customer_id", "member_id", "email", "phone",
               "name_customer", "address", "zip", "utm_content", "token", "transcript", "message"}
PATTERNS = {
    "UUID": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    "メール": r"[\w.+-]+@[\w-]+\.[\w.]+",
    "電話番号": r"0\d{1,4}-?\d{1,4}-?\d{3,4}\b",
    "注文番号(#1234)": r"#\d{3,}",
    "郵便番号": r"\b\d{3}-\d{4}\b",
    "長い数字ID": r"\b\d{9,}\b",
    "URL": r"https?://",
}

def walk(o, path="$"):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from ((f"{path}.{k}", "key", k) for _ in [0] if k.lower() in BANNED_KEYS)
            yield from walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(o, str):
        for label, p in PATTERNS.items():
            if re.search(p, o, re.I):
                yield (path, label, o)

data = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "data.json"))
hits = list(walk(data))
for h in hits:
    print("NG", *h)
print("OK: 個資・ID なし" if not hits else f"{len(hits)} 件 NG")
sys.exit(1 if hits else 0)
