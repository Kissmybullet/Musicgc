#  MongoDB collections for group-management features ported from LadyRezebb.
#  All collections live in the same database as the music bot (config.DB_NAME).

from typing import Optional
from pymongo import AsyncMongoClient
from src.logger import LOGGER
from ._config import config


class GroupDatabase:
    """MongoDB collections for group-management features."""

    def __init__(self, client: AsyncMongoClient):
        _db = client[config.DB_NAME]
        self.welcome_db = _db["welcome"]
        self.notes_db = _db["notes"]
        self.rules_db = _db["rules"]
        self.warns_db = _db["warns"]
        self.locks_db = _db["locks"]
        self.blacklist_db = _db["blacklist"]
        self.blacklist_stickers_db = _db["blacklist_stickers"]
        self.blacklist_users_db = _db["blacklist_users"]
        self.filters_db = _db["filters"]
        self.flood_db = _db["flood"]
        self.gban_db = _db["gbans"]
        self.gban_settings_db = _db["gban_settings"]
        self.feds_db = _db["federations"]
        self.approve_db = _db["approvals"]
        self.connection_db = _db["connections"]
        self.log_channel_db = _db["log_channels"]
        self.report_db = _db["reporting"]
        self.disable_db = _db["disabled_commands"]
        self.nightmode_db = _db["nightmode"]
        self.karma_db = _db["karma"]
        self.couples_db = _db["couples"]
        self.afk_db = _db["afk"]
        self.force_sub_db = _db["force_sub"]
        self.userinfo_db = _db["userinfo"]

    # ── Welcome ────────────────────────────────────────────────────
    async def get_welcome(self, chat_id: int) -> Optional[dict]:
        return await self.welcome_db.find_one({"_id": chat_id})

    async def set_welcome(self, chat_id: int, data: dict) -> None:
        await self.welcome_db.update_one({"_id": chat_id}, {"$set": data}, upsert=True)

    async def reset_welcome(self, chat_id: int) -> None:
        await self.welcome_db.delete_one({"_id": chat_id})

    # ── Notes ──────────────────────────────────────────────────────
    async def get_notes(self, chat_id: int) -> list:
        doc = await self.notes_db.find_one({"_id": chat_id})
        return doc.get("notes", {}) if doc else {}

    async def save_note(self, chat_id: int, name: str, data: dict) -> None:
        await self.notes_db.update_one(
            {"_id": chat_id}, {"$set": {f"notes.{name}": data}}, upsert=True
        )

    async def rm_note(self, chat_id: int, name: str) -> None:
        await self.notes_db.update_one(
            {"_id": chat_id}, {"$unset": {f"notes.{name}": ""}}
        )

    async def rm_all_notes(self, chat_id: int) -> None:
        await self.notes_db.delete_one({"_id": chat_id})

    # ── Rules ──────────────────────────────────────────────────────
    async def get_rules(self, chat_id: int) -> Optional[str]:
        doc = await self.rules_db.find_one({"_id": chat_id})
        return doc.get("rules") if doc else None

    async def set_rules(self, chat_id: int, rules: str) -> None:
        await self.rules_db.update_one(
            {"_id": chat_id}, {"$set": {"rules": rules}}, upsert=True
        )

    async def clear_rules(self, chat_id: int) -> None:
        await self.rules_db.delete_one({"_id": chat_id})

    # ── Warns ──────────────────────────────────────────────────────
    async def get_warns(self, chat_id: int, user_id: int) -> dict:
        doc = await self.warns_db.find_one({"_id": f"{chat_id}_{user_id}"})
        return doc if doc else {"warns": [], "count": 0}

    async def add_warn(self, chat_id: int, user_id: int, reason: str) -> int:
        key = f"{chat_id}_{user_id}"
        doc = await self.warns_db.find_one({"_id": key})
        warns = doc.get("warns", []) if doc else []
        warns.append({"reason": reason})
        count = len(warns)
        await self.warns_db.update_one(
            {"_id": key},
            {"$set": {"warns": warns, "count": count}},
            upsert=True,
        )
        return count

    async def reset_warns(self, chat_id: int, user_id: int) -> None:
        await self.warns_db.delete_one({"_id": f"{chat_id}_{user_id}"})

    async def get_warn_limit(self, chat_id: int) -> int:
        doc = await self.warns_db.find_one({"_id": f"limit_{chat_id}"})
        return doc.get("limit", 3) if doc else 3

    async def set_warn_limit(self, chat_id: int, limit: int) -> None:
        await self.warns_db.update_one(
            {"_id": f"limit_{chat_id}"}, {"$set": {"limit": limit}}, upsert=True
        )

    # ── Locks ──────────────────────────────────────────────────────
    async def get_locks(self, chat_id: int) -> dict:
        doc = await self.locks_db.find_one({"_id": chat_id})
        return doc.get("locks", {}) if doc else {}

    async def set_lock(self, chat_id: int, lock_type: str, locked: bool) -> None:
        await self.locks_db.update_one(
            {"_id": chat_id}, {"$set": {f"locks.{lock_type}": locked}}, upsert=True
        )

    # ── Blacklist ──────────────────────────────────────────────────
    async def get_blacklist(self, chat_id: int) -> list:
        doc = await self.blacklist_db.find_one({"_id": chat_id})
        return doc.get("words", []) if doc else []

    async def add_blacklist(self, chat_id: int, word: str) -> None:
        await self.blacklist_db.update_one(
            {"_id": chat_id}, {"$addToSet": {"words": word}}, upsert=True
        )

    async def rm_blacklist(self, chat_id: int, word: str) -> None:
        await self.blacklist_db.update_one({"_id": chat_id}, {"$pull": {"words": word}})

    async def rm_all_blacklist(self, chat_id: int) -> None:
        await self.blacklist_db.update_one({"_id": chat_id}, {"$set": {"words": []}})

    # ── Blacklist stickers ─────────────────────────────────────────
    async def get_blacklist_stickers(self, chat_id: int) -> list:
        doc = await self.blacklist_stickers_db.find_one({"_id": chat_id})
        return doc.get("stickers", []) if doc else []

    async def add_blacklist_sticker(self, chat_id: int, sticker: str) -> None:
        await self.blacklist_stickers_db.update_one(
            {"_id": chat_id}, {"$addToSet": {"stickers": sticker}}, upsert=True
        )

    async def rm_blacklist_sticker(self, chat_id: int, sticker: str) -> None:
        await self.blacklist_stickers_db.update_one(
            {"_id": chat_id}, {"$pull": {"stickers": sticker}}
        )

    # ── Blacklist users ────────────────────────────────────────────
    async def is_user_blacklisted(self, user_id: int) -> bool:
        return await self.blacklist_users_db.find_one({"_id": user_id}) is not None

    async def add_blacklist_user(self, user_id: int) -> None:
        await self.blacklist_users_db.update_one(
            {"_id": user_id}, {"$setOnInsert": {}}, upsert=True
        )

    async def rm_blacklist_user(self, user_id: int) -> None:
        await self.blacklist_users_db.delete_one({"_id": user_id})

    # ── Custom filters ─────────────────────────────────────────────
    async def get_filters(self, chat_id: int) -> dict:
        doc = await self.filters_db.find_one({"_id": chat_id})
        return doc.get("filters", {}) if doc else {}

    async def add_filter(self, chat_id: int, keyword: str, data: dict) -> None:
        await self.filters_db.update_one(
            {"_id": chat_id}, {"$set": {f"filters.{keyword}": data}}, upsert=True
        )

    async def rm_filter(self, chat_id: int, keyword: str) -> None:
        await self.filters_db.update_one(
            {"_id": chat_id}, {"$unset": {f"filters.{keyword}": ""}}
        )

    async def rm_all_filters(self, chat_id: int) -> None:
        await self.filters_db.delete_one({"_id": chat_id})

    # ── Anti-flood ─────────────────────────────────────────────────
    async def get_flood_settings(self, chat_id: int) -> dict:
        doc = await self.flood_db.find_one({"_id": chat_id})
        return doc if doc else {"limit": 0, "mode": "mute"}

    async def set_flood(self, chat_id: int, limit: int) -> None:
        await self.flood_db.update_one(
            {"_id": chat_id}, {"$set": {"limit": limit}}, upsert=True
        )

    async def set_flood_mode(self, chat_id: int, mode: str) -> None:
        await self.flood_db.update_one(
            {"_id": chat_id}, {"$set": {"mode": mode}}, upsert=True
        )

    # ── Global bans ────────────────────────────────────────────────
    async def is_gbanned(self, user_id: int) -> bool:
        return await self.gban_db.find_one({"_id": user_id}) is not None

    async def gban(self, user_id: int, name: str, reason: str) -> None:
        await self.gban_db.update_one(
            {"_id": user_id},
            {"$set": {"name": name, "reason": reason}},
            upsert=True,
        )

    async def ungban(self, user_id: int) -> None:
        await self.gban_db.delete_one({"_id": user_id})

    async def get_gban_list(self) -> list:
        return [doc async for doc in self.gban_db.find()]

    async def get_gban_setting(self, chat_id: int) -> bool:
        doc = await self.gban_settings_db.find_one({"_id": chat_id})
        return doc.get("setting", True) if doc else True

    async def set_gban_setting(self, chat_id: int, setting: bool) -> None:
        await self.gban_settings_db.update_one(
            {"_id": chat_id}, {"$set": {"setting": setting}}, upsert=True
        )

    # ── Federations ────────────────────────────────────────────────
    async def create_fed(self, fed_id: str, name: str, creator: int) -> None:
        await self.feds_db.update_one(
            {"_id": fed_id},
            {"$set": {"name": name, "creator": creator, "chats": [], "bans": []}},
            upsert=True,
        )

    async def get_fed(self, fed_id: str) -> Optional[dict]:
        return await self.feds_db.find_one({"_id": fed_id})

    async def get_user_feds(self, user_id: int) -> list:
        return [doc async for doc in self.feds_db.find({"creator": user_id})]

    async def del_fed(self, fed_id: str) -> None:
        await self.feds_db.delete_one({"_id": fed_id})

    async def join_fed(self, chat_id: int, fed_id: str) -> None:
        await self.feds_db.update_one(
            {"_id": fed_id}, {"$addToSet": {"chats": chat_id}}
        )

    async def leave_fed(self, chat_id: int, fed_id: str) -> None:
        await self.feds_db.update_one({"_id": fed_id}, {"$pull": {"chats": chat_id}})

    async def fed_ban(self, fed_id: str, user_id: int, reason: str) -> None:
        await self.feds_db.update_one(
            {"_id": fed_id},
            {"$addToSet": {"bans": {"user_id": user_id, "reason": reason}}},
        )

    # ── Cleaner ──────────────────────────────────────────────────
    async def get_cleaner_setting(self, chat_id: int) -> bool:
        doc = await self.userinfo_db.find_one({"_id": f"cleaner_{chat_id}"})
        # Note: I am reusing userinfo_db for cleaner settings, or we could add a dedicated collection
        return doc.get("enabled", False) if doc else False

    async def set_cleaner_setting(self, chat_id: int, enabled: bool) -> None:
        await self.userinfo_db.update_one(
            {"_id": f"cleaner_{chat_id}"}, {"$set": {"enabled": enabled}}, upsert=True
        )

    # ── Chatbot ──────────────────────────────────────────────────
    async def get_chatbot_setting(self, chat_id: int) -> bool:
        doc = await self.userinfo_db.find_one({"_id": f"chatbot_{chat_id}"})
        return doc.get("enabled", False) if doc else False

    async def set_chatbot_setting(self, chat_id: int, enabled: bool) -> None:
        await self.userinfo_db.update_one(
            {"_id": f"chatbot_{chat_id}"}, {"$set": {"enabled": enabled}}, upsert=True
        )

    # ── Disable Commands ──────────────────────────────────────────
    async def get_disabled_commands(self, chat_id: int) -> list:
        doc = await self.disable_db.find_one({"_id": chat_id})
        return doc.get("commands", []) if doc else []

    async def is_command_disabled(self, chat_id: int, cmd: str) -> bool:
        doc = await self.disable_db.find_one({"_id": chat_id})
        if not doc:
            return False
        return cmd in doc.get("commands", [])

    async def disable_command(self, chat_id: int, cmd: str) -> None:
        await self.disable_db.update_one(
            {"_id": chat_id}, {"$addToSet": {"commands": cmd}}, upsert=True
        )

    async def enable_command(self, chat_id: int, cmd: str) -> None:
        await self.disable_db.update_one(
            {"_id": chat_id}, {"$pull": {"commands": cmd}}
        )

    async def fed_unban(self, fed_id: str, user_id: int) -> None:
        await self.feds_db.update_one(
            {"_id": fed_id}, {"$pull": {"bans": {"user_id": user_id}}}
        )

    # ── Approve ────────────────────────────────────────────────────
    async def get_approved_users(self, chat_id: int) -> list:
        doc = await self.approve_db.find_one({"_id": chat_id})
        return doc.get("users", []) if doc else []

    async def approve_user(self, chat_id: int, user_id: int) -> None:
        await self.approve_db.update_one(
            {"_id": chat_id}, {"$addToSet": {"users": user_id}}, upsert=True
        )

    async def unapprove_user(self, chat_id: int, user_id: int) -> None:
        await self.approve_db.update_one(
            {"_id": chat_id}, {"$pull": {"users": user_id}}
        )

    async def unapprove_all(self, chat_id: int) -> None:
        await self.approve_db.update_one({"_id": chat_id}, {"$set": {"users": []}})

    async def is_approved(self, chat_id: int, user_id: int) -> bool:
        users = await self.get_approved_users(chat_id)
        return user_id in users

    # ── Connection ─────────────────────────────────────────────────
    async def get_connection(self, user_id: int) -> Optional[int]:
        doc = await self.connection_db.find_one({"_id": user_id})
        return doc.get("chat_id") if doc else None

    async def set_connection(self, user_id: int, chat_id: int) -> None:
        await self.connection_db.update_one(
            {"_id": user_id}, {"$set": {"chat_id": chat_id}}, upsert=True
        )

    async def rm_connection(self, user_id: int) -> None:
        await self.connection_db.delete_one({"_id": user_id})

    # ── Log channel ────────────────────────────────────────────────
    async def get_log_channel(self, chat_id: int) -> Optional[int]:
        doc = await self.log_channel_db.find_one({"_id": chat_id})
        return doc.get("log_channel") if doc else None

    async def set_log_channel(self, chat_id: int, log_channel: int) -> None:
        await self.log_channel_db.update_one(
            {"_id": chat_id}, {"$set": {"log_channel": log_channel}}, upsert=True
        )

    async def rm_log_channel(self, chat_id: int) -> None:
        await self.log_channel_db.delete_one({"_id": chat_id})

    # ── Reporting ──────────────────────────────────────────────────
    async def get_report_setting(self, chat_id: int) -> bool:
        doc = await self.report_db.find_one({"_id": chat_id})
        return doc.get("enabled", True) if doc else True

    async def set_report_setting(self, chat_id: int, enabled: bool) -> None:
        await self.report_db.update_one(
            {"_id": chat_id}, {"$set": {"enabled": enabled}}, upsert=True
        )

    # ── Disabled commands ──────────────────────────────────────────
    async def get_disabled_commands(self, chat_id: int) -> list:
        doc = await self.disable_db.find_one({"_id": chat_id})
        return doc.get("commands", []) if doc else []

    async def disable_command(self, chat_id: int, cmd: str) -> None:
        await self.disable_db.update_one(
            {"_id": chat_id}, {"$addToSet": {"commands": cmd}}, upsert=True
        )

    async def enable_command(self, chat_id: int, cmd: str) -> None:
        await self.disable_db.update_one({"_id": chat_id}, {"$pull": {"commands": cmd}})

    # ── Night mode ─────────────────────────────────────────────────
    async def get_nightmode(self, chat_id: int) -> Optional[dict]:
        return await self.nightmode_db.find_one({"_id": chat_id})

    async def set_nightmode(self, chat_id: int, data: dict) -> None:
        await self.nightmode_db.update_one(
            {"_id": chat_id}, {"$set": data}, upsert=True
        )

    async def rm_nightmode(self, chat_id: int) -> None:
        await self.nightmode_db.delete_one({"_id": chat_id})

    # ── Karma ──────────────────────────────────────────────────────
    async def get_karma(self, chat_id: int, user_id: int) -> int:
        doc = await self.karma_db.find_one({"_id": f"{chat_id}_{user_id}"})
        return doc.get("karma", 0) if doc else 0

    async def set_karma(self, chat_id: int, user_id: int, karma: int) -> None:
        await self.karma_db.update_one(
            {"_id": f"{chat_id}_{user_id}"},
            {"$set": {"karma": karma}},
            upsert=True,
        )

    async def update_karma(self, chat_id: int, user_id: int, delta: int) -> int:
        doc = await self.karma_db.find_one({"_id": f"{chat_id}_{user_id}"})
        current = doc.get("karma", 0) if doc else 0
        new_val = current + delta
        await self.karma_db.update_one(
            {"_id": f"{chat_id}_{user_id}"},
            {"$set": {"karma": new_val}},
            upsert=True,
        )
        return new_val

    async def get_karma_board(self, chat_id: int) -> list:
        cursor = (
            self.karma_db.find(
                {"_id": {"$regex": f"^{chat_id}_"}},
                {"_id": 1, "karma": 1},
            )
            .sort("karma", -1)
            .limit(10)
        )
        return await cursor.to_list(length=10)

    # ── Couples ────────────────────────────────────────────────────
    async def get_couple(self, chat_id: int, date: str) -> Optional[dict]:
        doc = await self.couples_db.find_one({"_id": chat_id})
        if doc:
            return doc.get("couples", {}).get(date)
        return None

    async def set_couple(self, chat_id: int, date: str, data: dict) -> None:
        await self.couples_db.update_one(
            {"_id": chat_id}, {"$set": {f"couples.{date}": data}}, upsert=True
        )

    # ── AFK ────────────────────────────────────────────────────────
    async def get_afk(self, user_id: int) -> Optional[dict]:
        return await self.afk_db.find_one({"_id": user_id})

    async def set_afk(self, user_id: int, data: dict) -> None:
        await self.afk_db.update_one({"_id": user_id}, {"$set": data}, upsert=True)

    async def rm_afk(self, user_id: int) -> None:
        await self.afk_db.delete_one({"_id": user_id})

    # ── Force subscribe ────────────────────────────────────────────
    async def get_fsub(self, chat_id: int) -> Optional[str]:
        doc = await self.force_sub_db.find_one({"_id": chat_id})
        return doc.get("channel") if doc else None

    async def set_fsub(self, chat_id: int, channel: str) -> None:
        await self.force_sub_db.update_one(
            {"_id": chat_id}, {"$set": {"channel": channel}}, upsert=True
        )

    async def rm_fsub(self, chat_id: int) -> None:
        await self.force_sub_db.delete_one({"_id": chat_id})

    # ── User info ──────────────────────────────────────────────────
    async def get_user_bio(self, user_id: int) -> Optional[str]:
        doc = await self.userinfo_db.find_one({"_id": user_id})
        return doc.get("bio") if doc else None

    async def set_user_bio(self, user_id: int, bio: str) -> None:
        await self.userinfo_db.update_one(
            {"_id": user_id}, {"$set": {"bio": bio}}, upsert=True
        )


group_db: Optional[GroupDatabase] = None


def init_group_db(client: AsyncMongoClient) -> GroupDatabase:
    global group_db
    group_db = GroupDatabase(client)
    return group_db
