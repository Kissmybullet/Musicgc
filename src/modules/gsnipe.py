#  Ported from LadyRezebb-reference/MukeshRobot/modules/snipe.py
#  Snipe: forward last deleted message from a chat

from pytdbot import Client, types

from src.core import DEV_USERS, OWNER_ID, Filter

__mod_name__ = "Snipe"
__help__ = """
<b>Snipe Commands (devs only):</b>
/snipe &lt;chat_id&gt; - Forward the last deleted message from specified chat
"""

_last_deleted: dict[int, types.Message] = {}


@Client.on_updateDeleteMessages()
async def deleted_msg_watcher(c: Client, update: types.UpdateDeleteMessages):
    chat_id = update.chat_id
    if chat_id > 0:
        return

    for msg_id in update.message_ids:
        try:
            result = await c.getMessage(chat_id=chat_id, message_id=msg_id)
            if isinstance(result, types.Error):
                continue
            if isinstance(result, types.Message):
                sender = result.sender_id
                if sender and isinstance(sender, types.MessageSenderUser):
                    if sender.user_id == c.me.id:
                        continue
                _last_deleted[chat_id] = result
        except Exception:
            pass


@Client.on_message(filters=Filter.command("snipe"))
async def snipe_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS:
        await message.reply_text("Only developers can use this command.")
        return

    args = message.text.split(None, 2)
    if len(args) < 2:
        await message.reply_text("Usage: /snipe &lt;chat_id&gt;")
        return

    try:
        target_chat = int(args[1])
    except ValueError:
        await message.reply_text("Invalid chat ID.")
        return

    last = _last_deleted.get(target_chat)
    if not last:
        await message.reply_text(
            f"No tracked deleted message for <code>{target_chat}</code>."
        )
        return

    text = (
        last.content.text.text if isinstance(last.content, types.MessageText) else None
    )
    caption = None
    if hasattr(last.content, "caption"):
        caption = last.content.caption

    if text:
        await message.reply_text(
            f"<b>Sniped from</b> <code>{target_chat}</code>:\n\n{text}"
        )
    elif caption:
        await message.reply_text(
            f"<b>Sniped from</b> <code>{target_chat}</code>:\n\n{caption}"
        )
    else:
        await message.reply_text(
            f"<b>Sniped from</b> <code>{target_chat}</code>: <i>(non-text message)</i>"
        )
