#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Common Chats"
__help__ = """
*✿ Common Chats ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /common ➛ Find common chats.
"""

@Client.on_message(filters=Filter.command(["common"]))
async def gcommonchats_cmd(c: Client, message: Message):
    """Find common chats."""
    await message.reply_text("Common Chats module is currently under construction! This feature will be available soon.")
