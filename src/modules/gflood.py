#  Ported from LadyRezebb-reference/MukeshRobot/modules/flood.py
#  Group management: Anti-flood protection

import html
import time
from collections import defaultdict
from typing import Optional

from pytdbot import Client, types

from src.core import Filter, group_db, WOLVES, TIGERS
from src.core._admins import is_admin, load_admin_cache
from src.modules._helpers import (
    ban_user,
    get_reply_user,
    get_user_id,
    get_user_mention,
    kick_user,
    mute_user,
)

__mod_name__ = "Flood"
__help__ = """
<b>Anti-flood Commands:</b>
/flood - Get current flood control setting
<b>Admins only:</b>
/setflood &lt;number/off&gt; - Enable or disable flood control
/setfloodmode &lt;ban/kick/mute/tban&gt; - Action when user exceeds flood limit
<b>Note:</b> Value must be filled for tban (e.g. 5m, 3h, 1d).
"""

_flood_cache: dict[int, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))


def extract_time(time_val: str) -> int:
    if not time_val:
        return 0
    unit = time_val[-1].lower()
    num = time_val[:-1]
    try:
        num = int(num)
    except ValueError:
        return 0
    if unit == "m":
        return num * 60
    elif unit == "h":
        return num * 3600
    elif unit == "d":
        return num * 86400
    elif unit == "w":
        return num * 604800
    return 0


@Client.on_message(filters=Filter.command("setflood"))
async def set_flood_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text(
            "Use <code>/setflood number</code> to enable anti-flood.\n"
            "Or use <code>/setflood off</code> to disable anti-flood!"
        )
        return

    val = args[1].strip().lower()
    if val in ("off", "no", "0"):
        await group_db.set_flood(chat_id, 0)
        await message.reply_text("Anti-flood has been disabled.")
        return

    if not val.isdigit():
        await message.reply_text(
            "Invalid argument. Please use a number, 'off' or 'no'."
        )
        return

    amount = int(val)
    if amount <= 0:
        await group_db.set_flood(chat_id, 0)
        await message.reply_text("Anti-flood has been disabled.")
        return

    if amount <= 3:
        await message.reply_text(
            "Anti-flood must be either 0 (disabled) or a number greater than 3!"
        )
        return

    await group_db.set_flood(chat_id, amount)
    await message.reply_text(
        f"Successfully updated anti-flood limit to <code>{amount}</code>!"
    )


@Client.on_message(filters=Filter.command("setfloodmode"))
async def set_flood_mode_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split(None, 1)
    if len(args) < 2:
        settings = await group_db.get_flood_settings(chat_id)
        mode = settings.get("mode", "mute")
        await message.reply_text(
            f"Current flood mode: <code>{mode}</code>\n"
            "Use <code>/setfloodmode ban/kick/mute/tban</code> to change."
        )
        return

    mode = args[1].strip().lower()
    valid_modes = ("ban", "kick", "mute", "tban")
    if mode not in valid_modes:
        await message.reply_text("I only understand ban/kick/mute/tban!")
        return

    if mode == "tban":
        await group_db.set_flood_mode(chat_id, "tban")
    else:
        await group_db.set_flood_mode(chat_id, mode)

    await message.reply_text(
        f"Exceeding consecutive flood limit will result in <b>{mode}</b>!"
    )


@Client.on_message(filters=Filter.command("flood"))
async def flood_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    settings = await group_db.get_flood_settings(chat_id)
    limit = settings.get("limit", 0)
    if limit == 0:
        await message.reply_text("I'm not enforcing any flood control here!")
    else:
        await message.reply_text(
            f"I'm currently restricting members after <code>{limit}</code> consecutive messages."
        )


async def check_flood(c: Client, message: types.Message):
    user_id = message.from_id
    chat_id = message.chat_id

    if not user_id:
        return

    if chat_id > 0:
        return

    if await is_admin(c, chat_id, user_id):
        _flood_cache[chat_id].pop(user_id, None)
        return

    if user_id in WOLVES or user_id in TIGERS:
        _flood_cache[chat_id].pop(user_id, None)
        return

    approved_users = await group_db.get_approved_users(chat_id)
    if user_id in approved_users:
        _flood_cache[chat_id].pop(user_id, None)
        return

    settings = await group_db.get_flood_settings(chat_id)
    limit = settings.get("limit", 0)
    if limit == 0:
        return

    now = time.time()
    user_msgs = _flood_cache[chat_id][user_id]
    user_msgs.append(now)
    user_msgs[:] = [t for t in user_msgs if now - t < 5]

    if len(user_msgs) >= limit:
        _flood_cache[chat_id][user_id] = []
        mode = settings.get("mode", "mute")
        name = await get_user_mention(c, user_id)

        if mode == "ban":
            await ban_user(c, chat_id, user_id)
            await message.reply_text(f"Beep Boop! Boop Beep!\nBanned {name}!")
        elif mode == "kick":
            await kick_user(c, chat_id, user_id)
            await message.reply_text(f"Beep Boop! Boop Beep!\nKicked {name}!")
        elif mode == "mute":
            await mute_user(c, chat_id, user_id)
            await message.reply_text(f"Beep Boop! Boop Beep!\nMuted {name}!")
        elif mode == "tban":
            await ban_user(c, chat_id, user_id)
            await message.reply_text(f"Beep Boop! Boop Beep!\nBanned {name}!")
        else:
            await mute_user(c, chat_id, user_id)
            await message.reply_text(f"Beep Boop! Boop Beep!\nMuted {name}!")
