#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Debug"
__help__ = """
*✿ Debug ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /debug ➛ Enable debug mode.
"""

@Client.on_message(filters=Filter.command(["debug"]))
async def gdebug_cmd(c: Client, message: Message):
    """Enable debug mode."""
    await message.reply_text("Debug module is currently under construction! This feature will be available soon.")
