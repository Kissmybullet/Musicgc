#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Extra Mod"
__help__ = """
*✿ Extra Mod ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /extra ➛ Extra module features.
"""

@Client.on_message(filters=Filter.command(["extra"]))
async def gextramod_cmd(c: Client, message: Message):
    """Extra module features."""
    await message.reply_text("Extra Mod module is currently under construction! This feature will be available soon.")
