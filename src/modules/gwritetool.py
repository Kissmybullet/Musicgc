#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import requests
from pytdbot import Client, types
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Write Tool"
__help__ = """
*✿ Write Tool ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /write <text> ➛ Write text on paper.
"""

@Client.on_message(filters=Filter.command(["write"]))
async def gwritetool_cmd(c: Client, message: Message):
    """Write text on paper."""
    if message.reply_to_message_id:
        replied = await message.getRepliedMessage()
        if isinstance(replied, types.Error) or not replied.text:
            return await message.reply_text("Reply to a text message.")
        text = replied.text
    else:
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.reply_text("Please provide some text or reply to a message.")
        text = args[1]

    msg = await message.reply_text("`Please wait...,\n\nWriting your text...`", parse_mode="markdown")
    if isinstance(msg, types.Error):
        return

    try:
        url = f"https://apis.xditya.me/write?text={text}"
        
        bot_user = await c.getMe()
        bot_name = bot_user.first_name if not isinstance(bot_user, types.Error) else "Bot"
        bot_username = bot_user.usernames.active_usernames[0] if not isinstance(bot_user, types.Error) and getattr(bot_user, 'usernames', None) else "bot"
        
        caption = f"""
sᴜᴄᴇssғᴜʟʟʏ ᴡʀɪᴛᴛᴇɴ ᴛᴇxᴛ 💘
✨ **ᴡʀɪᴛᴛᴇɴ ʙʏ :** <a href="https://t.me/{bot_username}">{bot_name}</a>
🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** <a href='tg://user?id={message.sender_id}'>User</a>
"""
        await c.sendPhoto(
            chat_id=message.chat_id,
            photo=types.InputFileRemote(id=url),
            caption=caption,
            reply_to_message_id=message.id,
            parse_mode="html"
        )
        await c.deleteMessages(chat_id=message.chat_id, message_ids=[msg.id], revoke=True)
    except Exception as e:
        c.logger.warning(f"write tool error: {e}")
        await c.editTextMessage(
            chat_id=message.chat_id, 
            message_id=msg.id, 
            text="Failed to write text."
        )
