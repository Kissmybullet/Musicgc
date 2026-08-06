#  Compatibility config for ported LadyRezebb modules.
#  Provides env variables in the naming convention expected by
#  LadyRezebb-reference modules so they can import from here.

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int = 0) -> int:
    val = os.getenv(name)
    try:
        return int(val) if val else default
    except (TypeError, ValueError):
        return default


def _env_set(name: str) -> set:
    val = os.getenv(name, "")
    try:
        return {int(x) for x in val.split() if x.strip()}
    except ValueError:
        return set()


# ── Telegram API ──────────────────────────────────────────────────
API_ID: int = _env_int("API_ID")
API_HASH: str = os.getenv("API_HASH", "")
TOKEN: str = os.getenv("TOKEN", "")

# ── Owner / Logging ───────────────────────────────────────────────
OWNER_ID: int = _env_int("OWNER_ID")
EVENT_LOGS: Optional[int] = _env_int("LOGGER_ID") or None
SUPPORT_CHAT: str = os.getenv("SUPPORT_GROUP", "")

# ── Database ──────────────────────────────────────────────────────
MONGO_DB_URI: str = os.getenv("MONGO_URI", "")

# ── Permission tiers ──────────────────────────────────────────────
DRAGONS: list = list(_env_set("DRAGONS") | _env_set("DEV_USERS") | {OWNER_ID})
DEV_USERS: list = list(_env_set("DEV_USERS") | {OWNER_ID})
DEMONS: list = list(_env_set("DEMONS"))
TIGERS: list = list(_env_set("TIGERS"))
WOLVES: list = list(_env_set("WOLVES"))

# ── Group settings ────────────────────────────────────────────────
BL_CHATS: list = list(_env_set("BL_CHATS"))
ALLOW_CHATS: bool = os.getenv("ALLOW_CHATS", "True").lower() == "true"
ALLOW_EXCL: bool = os.getenv("ALLOW_EXCL", "True").lower() == "true"
DEL_CMDS: bool = os.getenv("DEL_CMDS", "True").lower() == "true"
INFOPIC: bool = os.getenv("INFOPIC", "True").lower() == "true"
STRICT_GBAN: bool = os.getenv("STRICT_GBAN", "True").lower() == "true"
TEMP_DOWNLOAD_DIRECTORY: str = os.getenv("DOWNLOADS_DIR", "./")
WORKERS: int = _env_int("WORKERS", 8)
START_IMG: str = os.getenv("START_IMG", "")

# ── API Keys (optional) ──────────────────────────────────────────
CASH_API_KEY: str = os.getenv("CASH_API_KEY", "")
TIME_API_KEY: str = os.getenv("TIME_API_KEY", "")

# ── Module loading ────────────────────────────────────────────────
LOAD: list = os.getenv("LOAD", "").split()
NO_LOAD: list = os.getenv("NO_LOAD", "").split()
