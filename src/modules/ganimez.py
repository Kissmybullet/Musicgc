#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Animez"
__help__ = """
*✿ Animez ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /anime <query> ➛ Search anime info.
"""

@Client.on_message(filters=Filter.command(["anime"]))
async def ganimez_cmd(c: Client, message: Message):
    """Search anime info."""
    await message.reply_text("Animez module is currently under construction! This feature will be available soon.")
