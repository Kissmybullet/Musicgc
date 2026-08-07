#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import random

from pytdbot import Client, types
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Wish"
__help__ = """
*✿ Wish ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /wish <text> ➛ Make a wish.
"""

GIF = (
    "https://telegra.ph/file/ef94f2f61aa4d9394ef23.mp4",
    "https://telegra.ph/file/b82442bf9ebc32534f7a2.mp4",
    "https://telegra.ph/file/70d43e136125f9c120d2e.mp4",
    "https://telegra.ph/file/45354d3e42982f8de78f4.mp4",
    "https://telegra.ph/file/a22a0930f069686a0c4ef.mp4",
)

@Client.on_message(filters=Filter.command(["wish"]))
async def gwish_cmd(c: Client, message: Message):
    """Make a wish."""
    if message.reply_to_message_id:
        mm = random.randint(1, 100)
        fire = "https://telegra.ph/file/cae00f6c0729da2a93315.mp4"
        try:
            await c.sendAnimation(
                chat_id=message.chat_id,
                animation=types.InputFileRemote(id=fire),
                caption=f"**Hey <a href='tg://user?id={message.sender_id}'>User</a>, use /wish (your wish) 🙃**",
                reply_to_message_id=message.reply_to_message_id,
                parse_mode="html",
            )
        except Exception as e:
            c.logger.warning(e)
            await message.reply_text("Oops, something went wrong! Please try again later.")
    else:
        mm = random.randint(1, 100)
        fire = random.choice(GIF)
        try:
            await c.sendAnimation(
                chat_id=message.chat_id,
                animation=types.InputFileRemote(id=fire),
                caption=f"**Hey <a href='tg://user?id={message.sender_id}'>User</a>, your wish has been cast.💜**\n__Chance of success ⭐ {mm}%__",
                reply_to_message_id=message.id,
                parse_mode="html",
            )
        except Exception as e:
            c.logger.warning(e)
            await message.reply_text("Oops, something went wrong! Please try again later.")
