#  Ported from LadyRezebb-reference/MukeshRobot/modules/muting.py
#  Group management: Mute, Unmute, Temp-mute, Delete-mute

import html
from datetime import datetime, timedelta

from pytdbot import Client, types

from src.core import Filter, db
from src.core._admins import is_admin, load_admin_cache
from src.modules._helpers import (
    get_reply_user,
    get_user_id,
    get_user_mention,
    is_user_admin_in_chat,
    mute_user,
    unmute_user,
    delete_message,
)

__mod_name__ = "Muting"
__help__ = """
<b>Mute Commands (admins only):</b>
/mute &lt;user&gt; - Mute a user (silence)
/unmute &lt;user&gt; - Unmute a user
/dmute &lt;user&gt; - Delete command + mute silently
/tmute &lt;user&gt; &lt;time&gt; - Temp mute (e.g. 30m, 2h, 1d)
"""


def extract_time(time_val: str) -> tuple[int, str]:
    if not time_val:
        return 0, ""
    unit = time_val[-1].lower()
    num = time_val[:-1]
    try:
        num = int(num)
    except ValueError:
        return 0, ""
    if unit == "m":
        return num * 60, f"{num} minutes"
    elif unit == "h":
        return num * 3600, f"{num} hours"
    elif unit == "d":
        return num * 86400, f"{num} days"
    return 0, ""


async def _check_mute(c, message, chat_id, user_id):
    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return None, None, None

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return None, None, None

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return None, None, None

    target_id = await get_reply_user(message)
    args = message.text.split(None, 2)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text("Reply to a user or provide a user ID/username.")
        return None, None, None

    if await is_user_admin_in_chat(c, chat_id, target_id):
        await message.reply_text("I can't mute an admin.")
        return None, None, None

    name = await get_user_mention(c, target_id)
    return target_id, name, args


@Client.on_message(filters=Filter.command("mute"))
async def mute_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id
    target_id, name, _ = await _check_mute(c, message, chat_id, user_id)
    if not target_id:
        return

    success = await mute_user(c, chat_id, target_id)
    if success:
        await message.reply_text(f"Muted {name}.")
    else:
        await message.reply_text("Failed to mute. Check my permissions.")


@Client.on_message(filters=Filter.command("unmute"))
async def unmute_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id
    target_id, name, _ = await _check_mute(c, message, chat_id, user_id)
    if not target_id:
        return

    success = await unmute_user(c, chat_id, target_id)
    if success:
        await message.reply_text(f"Unmuted {name}.")
    else:
        await message.reply_text("Failed to unmute. Check my permissions.")


@Client.on_message(filters=Filter.command("dmute"))
async def dmute_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id
    target_id, name, _ = await _check_mute(c, message, chat_id, user_id)
    if not target_id:
        return

    success = await mute_user(c, chat_id, target_id)
    if success:
        await delete_message(c, chat_id, message.id)
    else:
        pass


@Client.on_message(filters=Filter.command(["tmute", "tempmute"]))
async def tmute_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id
    target_id, name, args = await _check_mute(c, message, chat_id, user_id)
    if not target_id:
        return

    time_arg = args[2] if len(args) >= 3 else args[1] if len(args) == 2 else ""
    seconds, time_str = extract_time(time_arg)

    if not seconds:
        await message.reply_text("Invalid time format. Use e.g. 30m, 2h, 1d.")
        return

    until = int(datetime.now().timestamp() + seconds)
    success = await mute_user(c, chat_id, target_id, until_date=until)
    if success:
        await message.reply_text(f"Muted {name} for {time_str}.")
    else:
        await message.reply_text("Failed to mute. Check my permissions.")
