#!/usr/bin/env python3
"""结构化操作日志（JSONL）。

落盘位置：``<project>/.lightrag-ingest/logs/ops-YYYYMMDD.jsonl``，一行一个事件，
字段固定：``ts / run_id / command / step / action / status / detail / error /
suggestion / duration_ms``。固定字段是为了能直接 ``jq`` 过滤，而不是读一坨自由文本。

三条规则：

1. 只写项目目录内；``repo-src`` / ``lightrag`` / ``.venv`` / ``rag_storage`` 一律不写。
2. 落盘前脱敏：``sk-...``、``Bearer ...`` 一律替换成 ``***``——日志会被贴进工单和聊天。
3. 日志自身失败不能影响主流程：写不进去就降级到 stderr 提示一次。
"""

from __future__ import annotations

import json
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]+"),
)


def _redact_text(text: str) -> str:
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("***", text)
    return text


def _redact(value):
    if isinstance(value, str):
        return _redact_text(value)
    if isinstance(value, dict):
        return {str(key): _redact(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    return value


class OpsLog:
    """一次命令执行一个 run_id，每个步骤一条事件。"""

    def __init__(self, project_dir: Path, command: str):
        self.run_id = f"{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
        self.command = command
        self.project_dir = Path(project_dir).resolve()
        log_dir = self.project_dir / ".lightrag-ingest" / "logs"
        self.path = log_dir / f"ops-{datetime.now():%Y%m%d}.jsonl"
        self._started = time.time()
        self._warned = False
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self._warn(exc)

    def _warn(self, exc: Exception) -> None:
        if not self._warned:
            print(f"[ops-log] 无法写入日志 {self.path}：{exc}", file=sys.stderr)
            self._warned = True

    def log(
        self,
        step: str,
        action: str,
        status: str = "ok",
        *,
        detail=None,
        error: str | None = None,
        suggestion: str | None = None,
        duration_ms: int | None = None,
    ) -> dict:
        event = {
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
            "run_id": self.run_id,
            "command": self.command,
            "step": step,
            "action": action,
            "status": status,
        }
        if detail is not None:
            event["detail"] = _redact(detail)
        if error:
            event["error"] = _redact_text(str(error))
        if suggestion:
            event["suggestion"] = _redact_text(str(suggestion))
        if duration_ms is None:
            duration_ms = int((time.time() - self._started) * 1000)
        event["duration_ms"] = duration_ms
        try:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError as exc:
            self._warn(exc)
        return event

    def note(self, text: str, *, detail=None) -> dict:
        """记录一次用户决策或人工批注。"""
        return self.log("decision", "note", detail={"note": text, **(detail or {})})


def read_events(path: Path, limit: int = 50) -> list[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    events = []
    for line in lines[-limit:]:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events
