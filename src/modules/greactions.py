#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Reactions"
__help__ = """
*✿ Reactions ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /reactions <on/off> ➛ Manage group reactions.
"""

@Client.on_message(filters=Filter.command(["reactions"]))
async def greactions_cmd(c: Client, message: Message):
    """Manage group reactions."""
    await message.reply_text("Reactions module is currently under construction! This feature will be available soon.")
