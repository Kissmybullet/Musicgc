#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Figlet"
__help__ = """
*✿ Figlet ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /figlet <text> ➛ Generate figlet text.
"""

@Client.on_message(filters=Filter.command(["figlet"]))
async def gfiglet_cmd(c: Client, message: Message):
    """Generate figlet text."""
    await message.reply_text("Figlet module is currently under construction! This feature will be available soon.")
