#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import asyncio
from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core import db
from src.core import admins_only

__mod_name__ = "Cleaner"
__help__ = """
*✿ Cʟᴇᴀɴᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /cleaner <on/off> ➛ Enable or disable auto-deletion of bot commands (blue text) in the chat.
"""


@Client.on_message(filters=Filter.command(["cleaner"]))
@admins_only(permissions="can_change_info")
async def cleaner_cmd(c: Client, message: Message):
    """Toggles cleaner in the chat."""
    chat_id = message.chat_id
    args = message.text.split()
    
    if len(args) < 2:
        current = await db.group.get_cleaner_setting(chat_id)
        status = "enabled" if current else "disabled"
        return await message.reply_text(f"Cleaner is currently **{status}**.\nUsage: `/cleaner on` or `/cleaner off`", parse_mode="markdown")
        
    action = args[1].lower()
    if action in ["on", "yes", "true", "enable"]:
        await db.group.set_cleaner_setting(chat_id, True)
        await message.reply_text("Cleaner has been **enabled**. I will now delete all commands sent in this chat.", parse_mode="markdown")
    elif action in ["off", "no", "false", "disable"]:
        await db.group.set_cleaner_setting(chat_id, False)
        await message.reply_text("Cleaner has been **disabled**.", parse_mode="markdown")
    else:
        await message.reply_text("Invalid argument. Use `on` or `off`.")


@Client.on_message()
async def cleaner_listener(c: Client, message: Message):
    """Deletes command messages if cleaner is enabled."""
    if getattr(message, "chat_id", 0) >= 0:
        return
        
    text = getattr(message, "text", "")
    if not text:
        return
        
    # Check if it's a command
    if text.startswith("/") or text.startswith("!"):
        # Check if cleaner is enabled in this chat
        is_enabled = await db.group.get_cleaner_setting(message.chat_id)
        if is_enabled:
            # Sleep briefly to allow other plugins to process the command first
            await asyncio.sleep(2)
            try:
                await c.deleteMessages(chat_id=message.chat_id, message_ids=[message.id], revoke=True)
            except Exception:
                pass
