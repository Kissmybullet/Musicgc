#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import html
import time

from pytdbot import Client, types

from src.core import Filter, group_db

__mod_name__ = "AFK"
__help__ = """
<b>AFK Commands:</b>

• <code>/afk [reason]</code> — Set yourself as AFK
"""

_afk_mention_cache: dict = {}


@Client.on_message(filters=Filter.command("afk"))
async def afk_cmd(c: Client, message: types.Message) -> None:
    user_id = message.from_id
    text = message.text or ""
    parts = text.split(None, 1)
    reason = parts[1] if len(parts) > 1 else "No reason given"

    user = await c.getUser(user_id=user_id)
    name = user.first_name if not isinstance(user, types.Error) else str(user_id)

    await group_db.set_afk(
        user_id,
        {
            "reason": reason,
            "name": name,
            "time": int(time.time()),
        },
    )

    reply = await message.reply_text(
        f"💤 <b>{html.escape(name)}</b> is now AFK.\n📝 Reason: {html.escape(reason)}"
    )
    if isinstance(reply, types.Error):
        c.logger.warning(f"afk_cmd error: {reply.message}")


@Client.on_updateNewMessage(position=1)
async def afk_watcher(c: Client, update: types.UpdateNewMessage) -> None:
    message = update.message
    if not message:
        return

    chat_id = message.chat_id
    if chat_id > 0:
        return

    user_id = message.from_id

    # Check if the sender is AFK — if so, remove AFK status
    afk_data = await group_db.get_afk(user_id)
    if afk_data:
        name = afk_data.get("name", str(user_id))
        reason = afk_data.get("reason", "")
        afk_time = afk_data.get("time", int(time.time()))
        duration = int(time.time()) - afk_time

        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)

        duration_str = ""
        if hours > 0:
            duration_str += f"{hours}h "
        if minutes > 0:
            duration_str += f"{minutes}m "
        duration_str += f"{seconds}s"
        duration_str = duration_str.strip()

        await group_db.rm_afk(user_id)

        await message.reply_text(
            f"👋 <b>{html.escape(name)}</b> is no longer AFK!\n"
            f"⏱️ Was AFK for: <code>{duration_str}</code>"
        )
        return

    # Check if the message mentions any AFK user
    text_content = message.content
    if not isinstance(text_content, types.MessageText):
        return

    formatted_text = text_content.text
    entities = formatted_text.entities or []
    mentioned_ids = set()

    for entity in entities:
        entity_type = entity.type
        if isinstance(entity_type, types.TextEntityTypeMentionName):
            mentioned_ids.add(str(entity_type.user_id))
        elif isinstance(entity_type, types.TextEntityTypeMention):
            username = formatted_text.text[
                entity.offset : entity.offset + entity.length
            ].lstrip("@")
            mentioned_ids.add(username)

    for uid in list(mentioned_ids):
        afk_info = await group_db.get_afk(uid)
        if not afk_info:
            continue

        name = afk_info.get("name", str(uid))
        reason = afk_info.get("reason", "No reason given")
        afk_time = afk_info.get("time", int(time.time()))
        duration = int(time.time()) - afk_time

        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)

        duration_str = ""
        if hours > 0:
            duration_str += f"{hours}h "
        if minutes > 0:
            duration_str += f"{minutes}m "
        duration_str += f"{seconds}s"
        duration_str = duration_str.strip()

        cache_key = f"{chat_id}:{uid}"
        last_sent = _afk_mention_cache.get(cache_key, 0)
        if time.time() - last_sent < 300:
            continue

        _afk_mention_cache[cache_key] = time.time()
        mention = f'<a href="tg://user?id={uid}">{html.escape(name)}</a>'
        await message.reply_text(
            f"💤 <b>{mention}</b> is currently AFK!\n"
            f"📝 Reason: {html.escape(reason)}\n"
            f"⏱️ Since: <code>{duration_str}</code> ago"
        )
        break
