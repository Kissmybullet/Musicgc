#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import re
from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core import db
from src.core import admins_only

__mod_name__ = "Filters"
__help__ = """
*✿ Fɪʟᴛᴇʀꜱ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /filter <keyword> <reply> ➛ Adds a filter to the chat.
❍ /filters ➛ Lists all active filters.
❍ /stop <keyword> ➛ Stops a filter.
❍ /stopall ➛ Stops all filters in the chat.
"""


@Client.on_message(filters=Filter.command(["filter", "addfilter"]))
@admins_only()
async def add_filter_cmd(c: Client, message: Message):
    """Adds a filter to the group."""
    chat_id = message.chat_id
    args = message.text.split(maxsplit=2)
    
    if len(args) < 2:
        return await message.reply_text("You need to specify a keyword to filter!")
        
    keyword = args[1].lower()
    
    if len(args) > 2:
        filter_data = {"type": "text", "content": args[2]}
    elif message.reply_to_message_id:
        replied = await c.getMessage(chat_id, message.reply_to_message_id)
        if hasattr(replied, "text") and replied.text:
            filter_data = {"type": "text", "content": replied.text}
        else:
            return await message.reply_text("I can only save text filters right now.")
    else:
        return await message.reply_text("You need to provide text or reply to a message to save a filter!")
        
    await db.group.add_filter(chat_id, keyword, filter_data)
    await message.reply_text(f"Added filter for `{keyword}`.")


@Client.on_message(filters=Filter.command(["stop", "stopfilter"]))
@admins_only()
async def stop_filter_cmd(c: Client, message: Message):
    """Removes a filter from the group."""
    chat_id = message.chat_id
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await message.reply_text("You need to specify a keyword to stop filtering!")
        
    keyword = args[1].lower()
    filters = await db.group.get_filters(chat_id)
    
    if keyword not in filters:
        return await message.reply_text(f"No filter found for `{keyword}`.")
        
    await db.group.rm_filter(chat_id, keyword)
    await message.reply_text(f"Stopped filter for `{keyword}`.")


@Client.on_message(filters=Filter.command(["filters", "activefilters"]))
async def list_filters(c: Client, message: Message):
    """Lists all active filters in the group."""
    chat_id = message.chat_id
    filters = await db.group.get_filters(chat_id)
    
    if not filters:
        return await message.reply_text("There are no active filters in this chat.")
        
    text = f"**Active filters in this chat:**\n"
    for keyword in filters.keys():
        text += f" - `{keyword}`\n"
        
    await message.reply_text(text, parse_mode="markdown")


@Client.on_message(filters=Filter.command(["stopall"]))
@admins_only()
async def stop_all_filters(c: Client, message: Message):
    """Removes all filters from the group."""
    chat_id = message.chat_id
    await db.group.rm_all_filters(chat_id)
    await message.reply_text("Stopped all filters in this chat.")


# Check incoming messages for filters
@Client.on_message()
async def check_filters(c: Client, message: Message):
    """Listens to regular messages and triggers filters if they match."""
    if getattr(message, "chat_id", 0) >= 0:
        return
    if not getattr(message, "text", None):
        return
        
    # Don't trigger on commands
    if message.text.startswith("/") or message.text.startswith("!"):
        return

    chat_id = message.chat_id
    filters = await db.group.get_filters(chat_id)
    
    if not filters:
        return

    text = message.text.lower()
    
    # Check if any filter keyword is in the text
    for keyword, data in filters.items():
        # Match whole words to avoid partial matching triggering unexpectedly
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text):
            if data["type"] == "text":
                await message.reply_text(data["content"])
                break  # Only trigger one filter per message
