#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Carbon"
__help__ = """
*✿ Carbon ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /carbon <text> ➛ Create code snippets.
"""

@Client.on_message(filters=Filter.command(["carbon"]))
async def gcarbon_cmd(c: Client, message: Message):
    """Create code snippets."""
    await message.reply_text("Carbon module is currently under construction! This feature will be available soon.")
