#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client, types
from pytdbot.types import Message
from src.core import Filter, config

__mod_name__ = "Bug"
__help__ = """
*✿ Bᴜɢ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /bug <message> ➛ Report a bug or issue directly to the bot owner/support chat.
"""


@Client.on_message(filters=Filter.command(["bug"]))
async def bug_cmd(c: Client, message: Message):
    """Reports a bug to the support group/log channel."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("Please provide a detailed description of the bug you found.")
        
    bug_text = args[1]
    sender_name = "Unknown User"

    user = await c.getUser(user_id=message.from_id)
    # print(user)
    if not isinstance(user, types.Error):
        sender_name = user.first_name

        
    chat_name = "Private Chat"
    if message.chat_id < 0:
        chat = await c.getChat(chat_id=message.chat_id)
        p
        if not isinstance(chat, types.Error):
            chat_name = chat.title
            
    report_msg = (
        f"🚨 **New Bug Report!**\n\n"
        f"**From User:** {sender_name} (`{message.from_id}`)\n"
        f"**From Chat:** {chat_name} (`{message.chat_id}`)\n\n"
        f"**Report:**\n`{bug_text}`"
    )
    
    # Send to support chat or log channel
    target = config.LOG_CHAT_ID
    if target:
        res = await c.sendTextMessage(target, report_msg, parse_mode="markdown")
        if not isinstance(res, types.Error):
            await message.reply_text("Bug report successfully submitted to the developers! Thank you.", parse_mode="markdown")
        else:
            await message.reply_text("Failed to send bug report. Please join the support chat to report it manually.")
    else:
        await message.reply_text("Log channel not configured. Cannot send bug report.")
