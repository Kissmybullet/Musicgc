#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
import urllib.parse

__mod_name__ = "Logo"
__help__ = """
*✿ Lᴏɢᴏ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /logo <text> ➛ Generates a simple logo from the given text.
"""


@Client.on_message(filters=Filter.command(["logo"]))
async def glogo_cmd(c: Client, message: Message):
    """Generates a logo."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("Please provide some text to generate a logo.")

    text = args[1]
    encoded_text = urllib.parse.quote(text)

    msg = await message.reply_text("🎨 Generating logo...")

    # Using a free placeholder logo API that is highly reliable
    logo_url = f"https://dummyimage.com/800x800/121212/00ffcc.png&text={encoded_text}"

    try:
        reply = await message.reply_photo(
            photo=logo_url,
            caption=f"🎨 **Logo generated for:** `{text}`",
            parse_mode="markdown",
        )
        if isinstance(reply, types.Error):
            await c.editTextMessage(
                chat_id=message.chat_id,
                message_id=msg.id,
                text="Failed to generate logo.",
                parse_mode="html",
            )
        else:
            await c.deleteMessages(
                chat_id=message.chat_id, message_ids=[msg.id], revoke=True
            )
    except Exception as e:
        await c.editTextMessage(
            chat_id=message.chat_id,
            message_id=msg.id,
            text=f"Error generating logo: {str(e)}",
            parse_mode="html",
        )
