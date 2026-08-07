#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Hidden"
__help__ = """
*✿ Hidden ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /hide <text> ➛ Manage hidden messages.
"""

@Client.on_message(filters=Filter.command(["hide"]))
async def ghidden_cmd(c: Client, message: Message):
    """Manage hidden messages."""
    await message.reply_text("Hidden module is currently under construction! This feature will be available soon.")
