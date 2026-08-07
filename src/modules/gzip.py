#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Zip"
__help__ = """
*✿ Zip ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /zip ➛ Zip files.
"""

@Client.on_message(filters=Filter.command(["zip"]))
async def gzip_cmd(c: Client, message: Message):
    """Zip files."""
    await message.reply_text("Zip module is currently under construction! This feature will be available soon.")
