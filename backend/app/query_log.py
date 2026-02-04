import json
import logging
import re
import threading
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_COUNTS_FILE = _LOG_DIR / "history.json"

_logger = logging.getLogger(__name__)

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")

_counts: dict[str, dict[str, int]] = {"queries": {}, "sido": {}, "sigungu": {}}
_counts_lock = threading.Lock()
_QUERIES_MAX = 1000
_WRITE_EVERY = 10
_write_counter = 0


def setup():
    """Load persisted query counts."""
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        if _COUNTS_FILE.exists():
            raw = json.loads(_COUNTS_FILE.read_text(encoding="utf-8"))
            for section in _counts:
                _counts[section].update(raw.get(section, {}))
    except Exception as e:
        for section in _counts.values():
            section.clear()
        _logger.warning(
            "Failed to load query counts from %s, starting fresh: %s",
            _COUNTS_FILE,
            e,
        )


def shutdown():
    """Flush pending counts to disk on app shutdown."""
    with _counts_lock:
        snapshot = {s: dict(c) for s, c in _counts.items()}
    _flush(snapshot)


def _sanitize(value: str | None) -> str:
    """Strip ANSI escapes and non-printable characters to prevent log injection."""
    if value is None:
        return "-"
    return "".join(ch for ch in _ANSI_RE.sub("", value) if ch.isprintable())


def _flush(snapshot: dict[str, dict[str, int]]):
    """Write a counts snapshot to disk."""
    _COUNTS_FILE.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def log_query(query: str, sido: str | None, sigungu: str | None, results: list[dict]):
    """Log search query and top results to the query log."""
    top_names = ", ".join(r["name"] for r in results[:5])
    _logger.info(
        'query="%s" sido=%s sigungu=%s results=[%s]',
        _sanitize(query),
        _sanitize(sido),
        _sanitize(sigungu),
        top_names,
    )


def record_query(query: str, sido: str | None, sigungu: str | None):
    """Record query counts and persist to history file."""
    global _write_counter
    raw = {"queries": query, "sido": sido, "sigungu": sigungu}
    fields = {k: _sanitize(v) for k, v in raw.items() if v is not None}

    snapshot = None
    with _counts_lock:
        queries = _counts["queries"]
        if fields["queries"] not in queries and len(queries) >= _QUERIES_MAX:
            del queries[min(queries, key=queries.__getitem__)]

        for section, value in fields.items():
            _counts[section][value] = _counts[section].get(value, 0) + 1

        _write_counter += 1
        if _write_counter >= _WRITE_EVERY:
            snapshot = {s: dict(c) for s, c in _counts.items()}
            _write_counter = 0

    if snapshot is not None:
        _flush(snapshot)
