import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
EXAMPLES_DIR = ROOT_DIR / "examples"

DATAHUB_MCP_URL = os.environ.get("DATAHUB_MCP_URL", "")
DATAHUB_MCP_TOKEN = os.environ.get("DATAHUB_MCP_TOKEN", "")
MODEL = os.environ.get("DATADOC_MODEL", "")


def require_config() -> None:
    if not DATAHUB_MCP_URL:
        raise RuntimeError(
            "Missing required env var: DATAHUB_MCP_URL. Copy .env.example to .env and fill it in."
        )
