#  Ported from LadyRezebb-reference/MukeshRobot/modules/warns.py
#  Group management: Warn, Unwarn, MyWarns, WarnLimit

import html

from pytdbot import Client, types

from src.core import Filter, group_db
from src.core._admins import is_admin, is_owner, load_admin_cache
from src.modules._helpers import (
    ban_user,
    get_reply_user,
    get_user_id,
    get_user_mention,
    is_user_admin_in_chat,
    send_message,
)

__mod_name__ = "Warns"
__help__ = """
<b>Warn Commands:</b>
/warn &lt;user&gt; &lt;reason&gt; - Warn a user
/unwarn &lt;user&gt; - Remove all warns from a user
/mywarns - Check your own warns
/warnlimit &lt;n&gt; - Set the warn limit (default 3)

When a user reaches the warn limit, they will be automatically banned.
"""


@Client.on_message(filters=Filter.command("warn"))
async def warn_cmd(c: Client, message: types.Message):
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
        await message.reply_text("I can't warn an admin.")
        return

    reason = ""
    if message.reply_to_message_id and len(args) >= 2:
        reason = args[1]
    elif len(args) >= 3:
        reason = args[2]
    elif len(args) >= 2 and not message.reply_to_message_id:
        reason = args[1]

    warn_data = await group_db.add_warn(chat_id, target_id, reason)
    limit = await group_db.get_warn_limit(chat_id)
    name = await get_user_mention(c, target_id)
    warner = await get_user_mention(c, user_id)

    if warn_data >= limit:
        await group_db.reset_warns(chat_id, target_id)
        success = await ban_user(c, chat_id, target_id)

        if success:
            warns_info = await group_db.get_warns(chat_id, target_id)
            reasons = [w.get("reason", "") for w in warns_info.get("warns", [])]
            text = (
                f"<b>Ban Event</b>\n"
                f"<b>User:</b> {name}\n"
                f"<b>Count:</b> {warn_data}/{limit}\n"
                f"<b>Banned by:</b> {warner}"
            )
            for r in reasons:
                if r:
                    text += f"\n  - {html.escape(r)}"
            await message.reply_text(text)
        else:
            await message.reply_text("Failed to ban. Check my permissions.")
    else:
        text = (
            f"<b>Warn Event</b>\n"
            f"<b>User:</b> {name}\n"
            f"<b>Count:</b> {warn_data}/{limit}\n"
            f"<b>Warned by:</b> {warner}"
        )
        if reason:
            text += f"\n<b>Reason:</b> {html.escape(reason)}"
        await message.reply_text(text)


@Client.on_message(filters=Filter.command("unwarn"))
async def unwarn_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    target_id = await get_reply_user(message)
    args = message.text.split(None, 2)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text("Reply to a user or provide a user ID/username.")
        return

    warn_data = await group_db.get_warns(chat_id, target_id)
    if warn_data.get("count", 0) == 0:
        await message.reply_text("This user doesn't have any warns!")
        return

    await group_db.reset_warns(chat_id, target_id)
    name = await get_user_mention(c, target_id)
    await message.reply_text(f"Warns have been reset for {name}.")


@Client.on_message(filters=Filter.command("mywarns"))
async def mywarns_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    target_id = await get_reply_user(message)
    if not target_id:
        target_id = user_id

    warn_data = await group_db.get_warns(chat_id, target_id)
    count = warn_data.get("count", 0)
    warns = warn_data.get("warns", [])
    limit = await group_db.get_warn_limit(chat_id)

    if count == 0:
        await message.reply_text("You have no warns!")
        return

    name = await get_user_mention(c, target_id)
    text = f"{name} has <b>{count}/{limit}</b> warns.\n"

    for w in warns:
        reason = w.get("reason", "No reason")
        text += f"\n  • {html.escape(reason)}"

    await message.reply_text(text)


@Client.on_message(filters=Filter.command("warnlimit"))
async def warnlimit_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split()

    if len(args) >= 2:
        if args[1].isdigit():
            new_limit = int(args[1])
            if new_limit < 3:
                await message.reply_text("The minimum warn limit is 3!")
                return
            await group_db.set_warn_limit(chat_id, new_limit)
            await message.reply_text(f"Warn limit set to <b>{new_limit}</b>.")
        else:
            await message.reply_text("Please provide a valid number.")
    else:
        limit = await group_db.get_warn_limit(chat_id)
        await message.reply_text(f"The current warn limit is <b>{limit}</b>.")
