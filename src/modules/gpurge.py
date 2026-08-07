#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import asyncio

from pytdbot import Client, types

from src.core import Filter, admins_only

__mod_name__ = "Purge"
__help__ = """
<b>Purge Commands:</b>
• <code>/del</code> — Delete the replied message
• <code>/purge</code> — Delete all messages from the replied message up to the current one
"""


@Client.on_message(filters=Filter.command("del"))
@admins_only()
async def delete_cmd(c: Client, message: types.Message):
    """Deletes the replied message."""
    chat_id = message.chat_id

    if not message.reply_to_message_id:
        reply = await message.reply_text("Reply to a message to delete it.")
        if not isinstance(reply, types.Error):
            await asyncio.sleep(3)
            await c.deleteMessages(
                chat_id=chat_id, message_ids=[reply.id, message.id], revoke=True
            )
        return

    # Delete both the command message and the replied message
    await c.deleteMessages(
        chat_id=chat_id,
        message_ids=[message.reply_to_message_id, message.id],
        revoke=True,
    )


@Client.on_message(filters=Filter.command("purge"))
@admins_only()
async def purge_cmd(c: Client, message: types.Message):
    """Purges messages from the replied message to the command message."""
    chat_id = message.chat_id

    if not message.reply_to_message_id:
        reply = await message.reply_text("Reply to a message to start purging.")
        if not isinstance(reply, types.Error):
            await asyncio.sleep(3)
            await c.deleteMessages(
                chat_id=chat_id, message_ids=[reply.id, message.id], revoke=True
            )
        return

    start_msg_id = message.reply_to_message_id
    end_msg_id = message.id

    if start_msg_id > end_msg_id:
        return

    # We generate potential message IDs (incrementing by 1048576)
    # and fetch them using getMessages to populate TDLib's local cache.
    # This prevents the 'Invalid message identifier' error.
    potential_ids = list(range(start_msg_id, end_msg_id + 1, 1048576))
    
    deleted_count = 0
    for i in range(0, len(potential_ids), 100):
        batch = potential_ids[i : i + 100]
        
        # 1. Ask TDLib to get messages (fetches from server and caches them)
        res = await c.getMessages(chat_id=chat_id, message_ids=batch)
        
        valid_ids = []
        if not isinstance(res, types.Error) and hasattr(res, "messages"):
            for m in res.messages:
                if m and hasattr(m, "id"):
                    valid_ids.append(m.id)
                    
        # 2. Now delete the valid ones that TDLib actually knows about
        if valid_ids:
            await c.deleteMessages(chat_id=chat_id, message_ids=valid_ids, revoke=True)
            deleted_count += len(valid_ids)

    # Send confirmation
    reply = await c.sendTextMessage(
        chat_id=chat_id, text=f"Purged {deleted_count} messages."
    )
    if not isinstance(reply, types.Error):
        await asyncio.sleep(3)
        await c.deleteMessages(chat_id=chat_id, message_ids=[reply.id], revoke=True)
