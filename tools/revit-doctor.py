"""Read-only native Revit installation and configured endpoint check (Python 3.11+)."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tomllib
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "native-revit.json").read_text(encoding="utf-8"))
    config_path = args.config or Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml"
    config = tomllib.loads(config_path.read_text(encoding="utf-8-sig")) if config_path.exists() else {}
    server = config.get("mcp_servers", {}).get(manifest["integration"], {})
    settings = server.get("env", {})
    local = Path(os.environ["LOCALAPPDATA"])
    url = settings.get("CODEX_NATIVE_REVIT_URL", manifest["default_url"])
    token_file = settings.get("CODEX_NATIVE_REVIT_TOKEN_FILE", str(local / manifest["token_path_under_localappdata"]))
    print(f"Selected repo release: {manifest['release']}")
    print(f"Config: {config_path}; server registered: {bool(server)}")
    print(f"Endpoint: {url}")
    if ":49328" in url:
        print("NOTICE: configured endpoint is the historical isolated test port.")
    addin = Path(os.environ["APPDATA"]) / "Autodesk/Revit/Addins/2025/CodexNativeRevit2025.addin"
    installed_ok = False
    if addin.exists():
        assembly_text = ET.parse(addin).findtext(".//Assembly")
        if assembly_text:
            assembly = Path(assembly_text.strip())
            if assembly.is_file():
                digest = hashlib.sha256(assembly.read_bytes()).hexdigest()
                installed_ok = digest == manifest["assembly_sha256"]
                print(f"Installed assembly matches selected release: {installed_ok}")
            else:
                print("Installed manifest points to a missing assembly.")
        else:
            print("Installed manifest has no assembly path.")
    else:
        print("Native add-in manifest is missing.")
    controller = root / manifest["controller"]
    spec = importlib.util.spec_from_file_location("native_revit_doctor_controller", controller)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Use the configured token file without displaying credentials. A direct token
    # is honored only when explicitly set in this server's own configuration.
    client = module.Client(base_url=url, token=settings.get("CODEX_NATIVE_REVIT_TOKEN"), token_file=token_file, timeout=3)
    client.token = settings.get("CODEX_NATIVE_REVIT_TOKEN")
    try:
        capabilities = client._request("GET", "/v1/capabilities")
    except module.ControllerError as exc:
        print(f"Connection unavailable: {exc.code}. No model operation was submitted.")
        return 1
    identity_ok = capabilities.get("identity") == manifest["integration"]
    print(f"Bridge identity matches: {identity_ok}; process ID: {capabilities.get('process_id')}")
    print("Next: verify that process, then submit documents.list and inspect its completed receipt.")
    return 0 if installed_ok and identity_ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, ET.ParseError):
        print("Diagnostic setup failed. Check config, manifest, controller, and Windows paths.", file=sys.stderr)
        sys.exit(2)
