"""Health check for the 1529 Wieland tile loop running in Chat On Steroids.

Read-only. Prints one JSON object and exits 0 (HEALTHY) or 1 (UNHEALTHY).
Run with: python tools/loop_health.py [--quiet-minutes 25]

It checks, from the CoS app log and state files:
  - the CoS app is alive (app.log written in the last 10 minutes)
  - the prime chat's Loop switch is still on
  - some tool call from the prime or a worker happened within --quiet-minutes
  - no stuck/pause/refusal markers since the last tool call
  - the Revit bridge answers
  - the loop ledger moved in the last 90 minutes (soft warning only)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

APPDATA = Path(os.environ["APPDATA"]) / "chat-on-steroids"
# The prime's CoS session id is stable; its ChatGPT conversation id changes when CoS runs
# Compact & Resume (seen 2026-11-06 12:21 UTC), so read the current one from the session record.
PRIME_SESSION = "88058fb9-0e8d-44f9-851d-b374ee9d4f42"


def current_prime_conversation() -> str:
    meta = json.loads((APPDATA / "sessions" / PRIME_SESSION / "meta.json").read_text(encoding="utf-8"))
    return str(meta["conversationId"])


PRIME_CONVERSATION = current_prime_conversation()
LOG = APPDATA / "app.log"
SWITCHES = APPDATA / "state" / "goal-switches.json"
LEDGER = Path(__file__).resolve().parent.parent / "state" / "LEDGER.md"
BRIDGE = "http://127.0.0.1:49327/v1/capabilities"
TOKEN = Path(os.environ.get("LOCALAPPDATA", "")) / "CodexNativeRevit" / "token"

LINE_TIME = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z)\s+(\w+)\s+(.*)$")
TOOL_OK = re.compile(r"\btool [a-z_]+ ok in \d+ ms")
# Markers that mean the loop is stuck or paused. Each is a CoS log phrase.
BAD_MARKERS = (
    "is not picked up",
    "gave up on resume",
    "cannot be matched to it",
    "automatic sends paused",
    "slow down",
    "access limit",
    "recovery sweep has not finished",
    "chat_still_working",
    "paused at context limit",
    "pausing Goal",
    "goal is met",
    "closed deliberately",
)


def tail_lines(path: Path, max_bytes: int = 1_500_000) -> list[str]:
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek(max(0, size - max_bytes))
        return handle.read().decode("utf-8", errors="replace").splitlines()


def parse_time(stamp: str) -> datetime:
    return datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet-minutes", type=float, default=25.0,
                        help="longest allowed gap since the last tool call (a deep-thinking turn can be quiet for 20)")
    opts = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    problems: list[str] = []
    warnings: list[str] = []
    facts: dict[str, object] = {"checked_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ")}

    # 1. CoS alive
    try:
        age_min = (now - datetime.fromtimestamp(LOG.stat().st_mtime, timezone.utc)).total_seconds() / 60
        facts["app_log_age_min"] = round(age_min, 1)
        if age_min > 10:
            problems.append(f"app.log not written for {age_min:.0f} min: CoS may be closed or the PC asleep")
    except OSError as exc:
        problems.append(f"cannot read app.log: {exc.strerror}")
        print(json.dumps({"verdict": "UNHEALTHY", "problems": problems, **facts}))
        return 1

    # 2. Loop switch
    try:
        switches = json.loads(SWITCHES.read_text(encoding="utf-8")).get("switches", [])
        entry = next((s for s in switches if s.get("conversationId") == PRIME_CONVERSATION), None)
        facts["loop_switch"] = entry
        if not entry or not entry.get("enabled") or entry.get("mode") != "loop":
            problems.append(f"Loop is not on for the prime chat: {entry}")
    except (OSError, ValueError) as exc:
        warnings.append(f"could not read goal-switches.json: {exc}")

    # 3. Recent tool activity and stuck markers
    lines = tail_lines(LOG)
    last_tool: datetime | None = None
    last_tool_index = -1
    for index, line in enumerate(lines):
        match = LINE_TIME.match(line)
        if match and TOOL_OK.search(match.group(3)):
            last_tool = parse_time(match.group(1))
            last_tool_index = index
    if last_tool is None:
        problems.append("no tool calls found in the recent app.log")
    else:
        gap = (now - last_tool).total_seconds() / 60
        facts["last_tool_call_utc"] = last_tool.strftime("%Y-%m-%dT%H:%M:%SZ")
        facts["minutes_since_last_tool_call"] = round(gap, 1)
        if gap > opts.quiet_minutes:
            problems.append(f"no tool call for {gap:.0f} min (limit {opts.quiet_minutes:.0f})")

    horizon = now - timedelta(minutes=45)
    markers: list[str] = []
    for index, line in enumerate(lines):
        match = LINE_TIME.match(line)
        if not match or parse_time(match.group(1)) < horizon:
            continue
        text = match.group(3)
        if any(marker in text for marker in BAD_MARKERS) and PRIME_CONVERSATION[:8] in text + " ":
            # Only count it if nothing worked after it: a marker followed by tool calls was recovered.
            if index > last_tool_index:
                markers.append(f"{match.group(1)} {text[:200]}")
    if markers:
        problems.append("stuck/pause markers after the last tool call")
        facts["markers"] = markers[-5:]

    # 4. Revit bridge
    try:
        token = TOKEN.read_text(encoding="utf-8").strip()
        request = urllib.request.Request(BRIDGE, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(request, timeout=10) as response:
            facts["revit_bridge"] = "ok" if response.status == 200 else f"http {response.status}"
    except urllib.error.HTTPError as exc:
        facts["revit_bridge"] = f"http {exc.code}"
        warnings.append(f"Revit bridge returned HTTP {exc.code}")
    except (urllib.error.URLError, OSError) as exc:
        facts["revit_bridge"] = "unreachable"
        warnings.append(f"Revit bridge unreachable: {exc}")

    # 5. Ledger movement (soft)
    try:
        ledger_age = (now - datetime.fromtimestamp(LEDGER.stat().st_mtime, timezone.utc)).total_seconds() / 60
        facts["ledger_age_min"] = round(ledger_age, 1)
        if ledger_age > 90:
            warnings.append(f"LEDGER.md not updated for {ledger_age:.0f} min")
    except OSError:
        warnings.append("LEDGER.md missing")

    verdict = "UNHEALTHY" if problems else "HEALTHY"
    print(json.dumps({"verdict": verdict, "problems": problems, "warnings": warnings, **facts}, indent=1))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
