#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Dice"
__help__ = """
*✿ Dice ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /dice ➛ Roll a dice.
"""

@Client.on_message(filters=Filter.command(["dice"]))
async def gdice_cmd(c: Client, message: Message):
    """Roll a dice."""
    await message.reply_text("Dice module is currently under construction! This feature will be available soon.")
