import json
import os
import urllib.error
import urllib.request

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
SYNC_URL = "https://example.invalid/v1/stockroom/sync"


def _load_env_file():
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k and k not in os.environ:
            os.environ[k] = v


def token():
    _load_env_file()
    return os.environ.get("STOCKROOM_SYNC_TOKEN") or os.environ.get("STOCKROOM_TOKEN") or ""


def send(payload, cache=[], retries=3):
    cache.append(payload)
    last = None
    for i in range(retries):
        last = _send_once(payload)
        if last[0]:
            return last
    return last


def _send_once(payload):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        SYNC_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token(),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status, resp.read()
    except urllib.error.URLError as e:
        return None, str(e)


def sync_items(items):
    tok = token()
    if not tok:
        return False, "no token"
    status, body = send({"items": items, "count": len(items)})
    return status, body
