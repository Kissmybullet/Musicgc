#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Wallpaper"
__help__ = """
*✿ Wallpaper ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /wall <query> ➛ Search wallpapers.
"""

@Client.on_message(filters=Filter.command(["wall"]))
async def gwallpaper_cmd(c: Client, message: Message):
    """Search wallpapers."""
    await message.reply_text("Wallpaper module is currently under construction! This feature will be available soon.")
