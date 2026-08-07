#  Ported from LadyRezebb-reference/MukeshRobot/modules/bans.py
#  Group management: Ban, Unban, Kick, Temp-ban commands

import html
from datetime import datetime, timedelta

from pytdbot import Client, types

from src.core import Filter, db, config
from src.core._admins import is_admin, is_owner, load_admin_cache
from src.modules._helpers import (
    ban_user,
    delete_message,
    get_reply_user,
    get_user_id,
    get_user_mention,
    get_user_name,
    is_user_admin_in_chat,
    send_message,
    unban_user,
)

__mod_name__ = "Bans"
__help__ = """
<b>Ban Commands (admins only):</b>
/ban &lt;user&gt; - Ban a user
/sban &lt;user&gt; - Silently ban (deletes msg + no reply)
/tban &lt;user&gt; &lt;time&gt; - Temp ban (e.g. 30m, 2h, 1d)
/unban &lt;user&gt; - Unban a user
/kick &lt;user&gt; - Kick a user out of the group
/kickme - Kick yourself (non-admin)
"""


def extract_time(time_val: str) -> tuple[int, str]:
    """Parse time string like '30m', '2h', '1d' into (seconds, unit)."""
    if not time_val:
        return 0, ""
    unit = time_val[-1].lower()
    num = time_val[:-1]
    try:
        num = int(num)
    except ValueError:
        return 0, ""
    if unit == "m":
        return num * 60, "minutes"
    elif unit == "h":
        return num * 3600, "hours"
    elif unit == "d":
        return num * 86400, "days"
    return 0, ""


@Client.on_message(filters=Filter.command(["ban", "sban"]))
async def ban_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    target_id = await get_reply_user(message)
    args = message.text.split(None, 2)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text("Reply to a user or provide a user ID/username.")
        return

    if await is_user_admin_in_chat(c, chat_id, target_id):
        await message.reply_text("I can't ban an admin. Demote them first.")
        return

    is_sban = message.text.split()[0].lower() == "/sban"

    success = await ban_user(c, chat_id, target_id)
    if success:
        name = await get_user_mention(c, target_id)
        if is_sban:
            await delete_message(c, chat_id, message.id)
        else:
            await message.reply_text(f"Banned {name}.")
    else:
        await message.reply_text("Failed to ban. Check my permissions.")


@Client.on_message(filters=Filter.command("tban"))
async def tban_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    target_id = await get_reply_user(message)
    args = message.text.split(None, 2)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text("Reply to a user or provide a user ID/username.")
        return

    if await is_user_admin_in_chat(c, chat_id, target_id):
        await message.reply_text("I can't ban an admin.")
        return

    time_arg = args[2] if len(args) >= 3 else args[1] if len(args) == 2 else ""
    seconds, unit = extract_time(time_arg)

    if not seconds:
        await message.reply_text("Invalid time format. Use e.g. 30m, 2h, 1d.")
        return

    until = int(datetime.now().timestamp() + seconds)
    success = await ban_user(c, chat_id, target_id)
    if success:
        name = await get_user_mention(c, target_id)
        await message.reply_text(f"Banned {name} for {unit}.")
    else:
        await message.reply_text("Failed to ban. Check my permissions.")


@Client.on_message(filters=Filter.command("kick"))
async def kick_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    target_id = await get_reply_user(message)
    args = message.text.split(None, 2)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text("Reply to a user or provide a user ID/username.")
        return

    if await is_user_admin_in_chat(c, chat_id, target_id):
        await message.reply_text("I can't kick an admin.")
        return

    await ban_user(c, chat_id, target_id)
    await unban_user(c, chat_id, target_id)
    name = await get_user_mention(c, target_id)
    await message.reply_text(f"Kicked {name}.")


@Client.on_message(filters=Filter.command("unban"))
async def unban_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    target_id = await get_reply_user(message)
    args = message.text.split(None, 2)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text("Reply to a user or provide a user ID/username.")
        return

    success = await unban_user(c, chat_id, target_id)
    if success:
        name = await get_user_mention(c, target_id)
        await message.reply_text(f"Unbanned {name}.")
    else:
        await message.reply_text("Failed to unban. Check my permissions.")


@Client.on_message(filters=Filter.command("kickme"))
async def kickme_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to kick you.")
        return

    if await is_user_admin_in_chat(c, chat_id, user_id):
        await message.reply_text("I can't kick an admin.")
        return

    await ban_user(c, chat_id, user_id)
    await unban_user(c, chat_id, user_id)
    await message.reply_text("As you wish.")
