import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
EXAMPLES_DIR = ROOT_DIR / "examples"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DATAHUB_MCP_URL = os.environ.get("DATAHUB_MCP_URL", "")
DATAHUB_MCP_TOKEN = os.environ.get("DATAHUB_MCP_TOKEN", "")
MODEL = os.environ.get("DATADOC_MODEL", "claude-sonnet-5")


def require_config() -> None:
    missing = [
        name
        for name, value in [
            ("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY),
            ("DATAHUB_MCP_URL", DATAHUB_MCP_URL),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(
            f"Missing required env vars: {', '.join(missing)}. Copy .env.example to .env and fill them in."
        )
