#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "GPS"
__help__ = """
*✿ GPS ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /gps <location> ➛ Get map locations.
"""

@Client.on_message(filters=Filter.command(["gps"]))
async def ggps_cmd(c: Client, message: Message):
    """Get map locations."""
    await message.reply_text("GPS module is currently under construction! This feature will be available soon.")
