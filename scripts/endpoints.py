"""Deployment-specific endpoints and credentials, kept out of source control.

Copy endpoints.example.json to endpoints.json (git-ignored) and fill in your own
gateway URL, local model servers, and token file path. The experiment code reads
everything deployment-specific from here; nothing else in the repo names a host.
"""
import json
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "endpoints.json"  # repo root
if not _PATH.exists():
    raise SystemExit(
        "endpoints.json not found. Copy endpoints.example.json to endpoints.json "
        "and fill in your gateway URL, model-server URLs, and token file path."
    )
EP = json.loads(_PATH.read_text())


def token() -> str:
    return Path(EP["token_file"]).expanduser().read_text().strip()
