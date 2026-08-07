#  Ported from LadyRezebb-reference/MukeshRobot/modules/blacklistusers.py
#  Blacklist users from using bot commands

import html

from pytdbot import Client, types

from src.core import DEV_USERS, DRAGONS, OWNER_ID, TIGERS, Filter, group_db
from src.core._admins import load_admin_cache
from src.modules._helpers import get_reply_user, get_user_id, get_user_mention

__mod_name__ = "BlacklistUsers"
__help__ = """
<b>Blacklist User Commands (devs only):</b>
/bl_user &lt;user&gt; - Blacklist a user from using commands
/unbl_user &lt;user&gt; - Remove user from blacklist
/bl_list - List all blacklisted users
"""

BLACKLIST_WHITELIST = [OWNER_ID] + DEV_USERS + DRAGONS + TIGERS


def _is_protected(user_id: int) -> bool:
    return user_id in BLACKLIST_WHITELIST


@Client.on_message(filters=Filter.command("bl_user"))
async def bl_user_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS:
        await message.reply_text("Only developers can use this command.")
        return

    target_id = await get_reply_user(message)
    args = message.text.split(None, 2)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text("I doubt that's a user.")
        return

    if target_id == c.me.id:
        await message.reply_text(
            "How am I supposed to do my work if I am ignoring myself?"
        )
        return

    if _is_protected(target_id):
        await message.reply_text("No! Noticing Disasters is my job.")
        return

    await group_db.add_blacklist_user(target_id)
    name = await get_user_mention(c, target_id)
    await message.reply_text(f"I shall ignore the existence of {name}!")


@Client.on_message(filters=Filter.command("unbl_user"))
async def unbl_user_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS:
        await message.reply_text("Only developers can use this command.")
        return

    target_id = await get_reply_user(message)
    args = message.text.split(None, 2)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text("I doubt that's a user.")
        return

    if target_id == c.me.id:
        await message.reply_text("I always notice myself.")
        return

    if await group_db.is_user_blacklisted(target_id):
        await group_db.rm_blacklist_user(target_id)
        name = await get_user_mention(c, target_id)
        await message.reply_text(f"*notices* {name}")
    else:
        await message.reply_text("I am not ignoring them at all though!")


@Client.on_message(filters=Filter.command("bl_list"))
async def bl_list_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS:
        await message.reply_text("Only developers can use this command.")
        return

    blacklist_users_col = group_db.blacklist_users_db
    cursor = blacklist_users_col.find()
    user_ids = [doc["_id"] async for doc in cursor]

    if not user_ids:
        await message.reply_text(
            "<b>Blacklisted Users:</b>\nNone is being ignored as of yet."
        )
        return

    text = "<b>Blacklisted Users:</b>\n"
    for uid in user_ids:
        name = await get_user_mention(c, uid)
        text += f"  \u2022 {name}\n"

    await message.reply_text(text)
