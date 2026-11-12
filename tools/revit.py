"""Run the native controller with this client's configured connection (Python 3.11+)."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.command:
        parser.error("provide a controller command: capabilities, submit, status, wait, cancel, batch, or stdio")
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "native-revit.json").read_text(encoding="utf-8"))
    config_path = args.config or Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml"
    config = tomllib.loads(config_path.read_text(encoding="utf-8-sig"))
    settings = config["mcp_servers"][manifest["integration"]].get("env", {})
    if not settings.get("CODEX_NATIVE_REVIT_URL") or not settings.get("CODEX_NATIVE_REVIT_TOKEN_FILE"):
        print("Set both native Revit URL and token-file path in the selected client config first.", file=sys.stderr)
        return 2
    env = os.environ.copy()
    # Prevent a parent process's stale bridge credentials from overriding this client.
    for key in tuple(env):
        if key.startswith("CODEX_NATIVE_REVIT_"):
            del env[key]
    env.update({k: str(v) for k, v in settings.items() if k.startswith("CODEX_NATIVE_REVIT_")})
    return subprocess.run([sys.executable, str(root / manifest["controller"]), *args.command], env=env).returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError):
        print("Cannot load native Revit configuration; run tools/revit-doctor.py and inspect docs/NATIVE-REVIT.md.", file=sys.stderr)
        sys.exit(2)
