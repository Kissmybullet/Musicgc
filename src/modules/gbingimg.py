#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Bing Image"
__help__ = """
*✿ Bing Image ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /bingimg <query> ➛ Search Bing Images.
"""

@Client.on_message(filters=Filter.command(["bingimg"]))
async def gbingimg_cmd(c: Client, message: Message):
    """Search Bing Images."""
    await message.reply_text("Bing Image module is currently under construction! This feature will be available soon.")
