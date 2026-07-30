"""Launch the DataHub MCP server against a local `datahub docker quickstart` instance.

Quickstart ships with default admin credentials (datahub/datahub) that only
work against a fresh local instance -- this mints a short-lived personal
access token from them each run instead of asking anyone to store one.

Usage:
    python scripts/run_local_datahub_mcp.py

Then set DATAHUB_MCP_URL=http://127.0.0.1:8000/mcp in your .env (no token
needed there -- the local MCP HTTP transport isn't itself authenticated,
only its calls back to GMS are).
"""

import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

FRONTEND_URL = os.environ.get("DATAHUB_FRONTEND_URL", "http://localhost:9002")
GMS_URL = os.environ.get("DATAHUB_GMS_URL", "http://localhost:8080")
ADMIN_USER = "datahub"
ADMIN_PASSWORD = "datahub"


def _post_json(url: str, payload: dict, cookie: str | None = None) -> tuple[dict, str | None]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"} | ({"Cookie": cookie} if cookie else {}),
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        cookies = resp.headers.get_all("Set-Cookie") or []
        cookie_header = "; ".join(c.split(";", 1)[0] for c in cookies) or None
        body = resp.read()
        return (json.loads(body) if body else {}), cookie_header


def mint_local_token() -> str:
    try:
        _, cookie = _post_json(f"{FRONTEND_URL}/logIn", {"username": ADMIN_USER, "password": ADMIN_PASSWORD})
    except urllib.error.URLError as e:
        raise SystemExit(
            f"Could not reach DataHub frontend at {FRONTEND_URL}. Is `datahub docker quickstart` running? ({e})"
        )

    mutation = (
        "mutation { createAccessToken(input: {type: PERSONAL, actorUrn: "
        f'"urn:li:corpuser:{ADMIN_USER}", duration: ONE_HOUR, name: "datadoc-local-mcp"}}) '
        "{ accessToken } }"
    )
    result, _ = _post_json(f"{FRONTEND_URL}/api/v2/graphql", {"query": mutation}, cookie=cookie)
    if "errors" in result:
        raise SystemExit(f"Failed to mint access token: {result['errors']}")
    return result["data"]["createAccessToken"]["accessToken"]


def main() -> None:
    token = mint_local_token()
    print("Minted a 1-hour local DataHub personal access token.", file=sys.stderr)
    print(f"Starting MCP server against {GMS_URL} ...", file=sys.stderr)
    print("Set DATAHUB_MCP_URL=http://127.0.0.1:8000/mcp in your .env once this is running.", file=sys.stderr)

    exe_dir = os.path.dirname(sys.executable)
    exe = shutil.which("mcp-server-datahub", path=exe_dir) or shutil.which("mcp-server-datahub")
    if exe is None:
        raise SystemExit(
            "mcp-server-datahub not found. Run this with the Python from the venv you "
            "`pip install mcp-server-datahub`'d into, e.g. .mcpserver-venv/Scripts/python.exe"
        )

    env = os.environ | {
        "DATAHUB_GMS_URL": GMS_URL,
        "DATAHUB_GMS_TOKEN": token,
        "TOOLS_IS_MUTATION_ENABLED": "true",
        "TOOLS_IS_USER_ENABLED": "true",
    }
    subprocess.run([exe, "--transport", "http"], env=env, check=True)


if __name__ == "__main__":
    main()
