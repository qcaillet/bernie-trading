#!/usr/bin/env python3
"""
Hook dispatcher.

Scan `events/pending/`, match each event to a handler in `hooks/handlers/on_<kind>.py`,
exec it, move event to `processed/` or `failed/`.

Designed to be:
- Run by a cron (every 2 min) for catchup
- Or called manually after emit_event()
"""

import importlib.util
import json
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "events"
PENDING = EVENTS / "pending"
PROCESSED = EVENTS / "processed"
FAILED = EVENTS / "failed"
HANDLERS = Path(__file__).resolve().parent / "handlers"

for d in (PENDING, PROCESSED, FAILED, HANDLERS):
    d.mkdir(parents=True, exist_ok=True)


def emit_event(kind: str, payload: dict, event_id: str | None = None) -> Path:
    """Public API to emit a new event from anywhere."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    eid = event_id or f"e_{ts}"
    name = f"{ts}_{eid}_{kind}.json"
    path_tmp = PENDING / f".tmp_{name}"
    path = PENDING / name
    data = {"kind": kind, "ts": datetime.now(timezone.utc).isoformat(), "event_id": eid, "payload": payload}
    path_tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    path_tmp.rename(path)
    print(f"[dispatcher] emitted {name}")
    return path


def _load_handler(kind: str):
    fp = HANDLERS / f"on_{kind}.py"
    if not fp.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"handler_{kind}", fp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "handle", None)


def process_all() -> dict:
    pending = sorted(PENDING.glob("*.json"))
    stats = {"processed": 0, "failed": 0, "skipped": 0}
    for ev_path in pending:
        if ev_path.name.startswith(".tmp_"):
            continue
        try:
            data = json.loads(ev_path.read_text())
            kind = data["kind"]
            handler = _load_handler(kind)
            if handler is None:
                print(f"[dispatcher] no handler for kind={kind}, skipping {ev_path.name}")
                # Move to failed avec note
                (FAILED / ev_path.name).write_text(ev_path.read_text())
                (FAILED / (ev_path.stem + ".error.log")).write_text(f"No handler for kind={kind}")
                ev_path.unlink()
                stats["failed"] += 1
                continue
            result = handler(data["payload"], data)
            (PROCESSED / ev_path.name).write_text(ev_path.read_text())
            if result is not None:
                (PROCESSED / (ev_path.stem + ".result.json")).write_text(json.dumps(result, indent=2, default=str))
            ev_path.unlink()
            stats["processed"] += 1
            print(f"[dispatcher] processed {ev_path.name}")
        except Exception as e:
            err = traceback.format_exc()
            (FAILED / ev_path.name).write_text(ev_path.read_text() if ev_path.exists() else "")
            (FAILED / (ev_path.stem + ".error.log")).write_text(err)
            if ev_path.exists():
                ev_path.unlink()
            stats["failed"] += 1
            print(f"[dispatcher] FAILED {ev_path.name}: {e}")
    return stats


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "emit":
        kind = sys.argv[2]
        payload = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        emit_event(kind, payload)
    else:
        s = process_all()
        print(json.dumps(s, indent=2))
