#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter, db, admins_only
from src.core._httpx import HttpxClient
import urllib.parse
import re

__mod_name__ = "Chatbot"
__help__ = """
*✿ Cʜᴀᴛʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /chatbot <on/off> ➛ Enable or disable AI chatbot for this group.
"""


@Client.on_message(filters=Filter.command(["chatbot"]))
@admins_only(permissions="can_change_info")
async def chatbot_cmd(c: Client, message: Message):
    """Toggles chatbot in the chat."""
    chat_id = message.chat_id
    args = message.text.split()
    
    if len(args) < 2:
        current = await db.group.get_chatbot_setting(chat_id)
        status = "enabled" if current else "disabled"
        return await message.reply_text(f"Chatbot is currently **{status}**.\nUsage: `/chatbot on` or `/chatbot off`", parse_mode="markdown")
        
    action = args[1].lower()
    if action in ["on", "yes", "true", "enable"]:
        await db.group.set_chatbot_setting(chat_id, True)
        await message.reply_text("Chatbot has been **enabled**. The bot will now reply to messages that mention it.", parse_mode="markdown")
    elif action in ["off", "no", "false", "disable"]:
        await db.group.set_chatbot_setting(chat_id, False)
        await message.reply_text("Chatbot has been **disabled**.", parse_mode="markdown")
    else:
        await message.reply_text("Invalid argument. Use `on` or `off`.")


@Client.on_message()
async def chatbot_listener(c: Client, message: Message):
    """Listens for mentions and replies if chatbot is enabled."""
    if getattr(message, "chat_id", 0) >= 0:
        return
        
    text = getattr(message, "text", "")
    if not text:
        return
        
    # Ignore commands
    if text.startswith("/") or text.startswith("!"):
        return
        
    is_enabled = await db.group.get_chatbot_setting(message.chat_id)
    if not is_enabled:
        return
        
    # Check if we should reply (mentioned or replied to)
    should_reply = False
    
    if message.reply_to_message_id:
        replied = await c.getMessage(message.chat_id, message.reply_to_message_id)
        if replied and getattr(replied, "from_id", None) == c.me.id:
            should_reply = True
            
    bot_username = getattr(c.me.usernames, "editable_username", "").lower()
    if bot_username and f"@{bot_username}" in text.lower():
        should_reply = True
        
    # Also reply if bot's first name is mentioned
    bot_name = c.me.first_name.lower()
    if bot_name in text.lower():
        should_reply = True
        
    if not should_reply:
        return
        
    # Clean up text
    query = text.replace(f"@{bot_username}", "").replace(bot_name, "").strip()
    if not query:
        query = "Hello"
        
    from pytdbot.types import ChatActionTyping
    await c.sendChatAction(chat_id=message.chat_id, action=ChatActionTyping())
    
    # Use a free public chatbot API (Simsimi or similar)
    encoded_query = urllib.parse.quote(query)
    api_url = f"https://api.simsimi.net/v2/?text={encoded_query}&lc=en"
    
    client = HttpxClient()
    response = await client.make_request(api_url)
    await client.close()
    
    if response and "success" in response:
        reply_text = response.get("success", "I don't know what to say.")
        await message.reply_text(reply_text)
    else:
        # Fallback response
        await message.reply_text("I'm sorry, my brain is taking a quick nap. Try again later!")
