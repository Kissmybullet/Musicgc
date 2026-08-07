#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import html
import re

from pytdbot import Client, types

from src.core import Filter, group_db

__mod_name__ = "Karma"
__help__ = """
<b>Karma Commands:</b>

• <code>/karma</code> — Check your karma in this group
• <code>/karmatop</code> — View the karma leaderboard

<b>Karma Triggers:</b>
Reply to a user's message with <code>+1</code>, <code>+</code>, <code>👍</code>, etc. to increase their karma.
Reply with <code>-1</code>, <code>-</code>, <code>👎</code>, etc. to decrease their karma.
"""

POSITIVE_PATTERN = r"^\s*(\+|\+1|👍|👍🏻|👍🏼|👍🏽|👍🏾|👍🏿|❤️|😍|🔥)\s*$"
NEGATIVE_PATTERN = r"^\s*(-\s*1|-|👎|👎🏻|👎🏼|👎🏽|👎🏾|👎🏿|💔|😭|😢)\s*$"

@Client.on_message(filters=Filter.regex(f"{POSITIVE_PATTERN}|{NEGATIVE_PATTERN}"))
async def handle_karma_reply(c: Client, message: types.Message) -> None:
    chat_id = message.chat_id
    if chat_id > 0:
        return

    if not message.reply_to_message_id:
        return

    text = Filter._extract_text(message)
    if not text:
        return

    delta = 0
    if re.match(POSITIVE_PATTERN, text, re.IGNORECASE):
        delta = 1
    elif re.match(NEGATIVE_PATTERN, text, re.IGNORECASE):
        delta = -1
    else:
        return

    replied_message = await c.getMessage(chat_id=chat_id, message_id=message.reply_to_message_id)
    if isinstance(replied_message, types.Error):
        return

    sender = replied_message.sender_id
    if not isinstance(sender, types.MessageSenderUser):
        return

    target_user_id = sender.user_id

    # Prevent self-karma
    if message.from_id == target_user_id:
        return

    new_karma = await group_db.update_karma(chat_id, target_user_id, delta)

    user = await c.getUser(user_id=target_user_id)
    name = user.first_name if not isinstance(user, types.Error) else str(target_user_id)

    action = "increased" if delta > 0 else "decreased"
    reply_text = f"⭐ <b>{html.escape(name)}</b>'s karma has been {action} to <b>{new_karma}</b>"
    
    reply = await message.reply_text(reply_text)
    if isinstance(reply, types.Error):
        c.logger.warning(f"handle_karma_reply error: {reply.message}")


@Client.on_message(filters=Filter.command("karma"))
async def karma_cmd(c: Client, message: types.Message) -> None:
    chat_id = message.chat_id
    if chat_id > 0:
        reply = await message.reply_text("ℹ️ Karma is only available in groups.")
        if isinstance(reply, types.Error):
            c.logger.warning(f"karma_cmd error: {reply.message}")
        return

    user_id = message.from_id
    karma = await group_db.get_karma(chat_id, user_id)

    user = await c.getUser(user_id=user_id)
    name = user.first_name if not isinstance(user, types.Error) else str(user_id)

    reply = await message.reply_text(
        f"⭐ <b>{html.escape(name)}</b>'s karma in this group: <b>{karma}</b>"
    )
    if isinstance(reply, types.Error):
        c.logger.warning(f"karma_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("karmatop"))
async def karmatop_cmd(c: Client, message: types.Message) -> None:
    chat_id = message.chat_id
    if chat_id > 0:
        reply = await message.reply_text("ℹ️ Karma is only available in groups.")
        if isinstance(reply, types.Error):
            c.logger.warning(f"karmatop_cmd error: {reply.message}")
        return

    board = await group_db.get_karma_board(chat_id)
    if not board:
        reply = await message.reply_text("ℹ️ No karma data found for this group.")
        if isinstance(reply, types.Error):
            c.logger.warning(f"karmatop_cmd error: {reply.message}")
        return

    medals = ["🥇", "🥈", "🥉"]
    text = "<b>⭐ Karma Leaderboard</b>\n\n"
    for i, entry in enumerate(board):
        _id = entry["_id"]
        user_id = int(_id.split("_", 1)[1]) if "_" in _id else 0
        karma = entry.get("karma", 0)
        medal = medals[i] if i < 3 else f"<code>{i + 1}.</code>"
        user = await c.getUser(user_id=user_id)
        name = user.first_name if not isinstance(user, types.Error) else str(user_id)
        text += f"{medal} <b>{html.escape(name)}</b> — <code>{karma}</code>\n"

    reply = await message.reply_text(text)
    if isinstance(reply, types.Error):
        c.logger.warning(f"karmatop_cmd error: {reply.message}")
