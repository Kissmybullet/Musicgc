#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "WebSS"
__help__ = """
*✿ WᴇʙSS ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /webss <url> ➛ Takes a screenshot of the given website.
"""


@Client.on_message(filters=Filter.command(["webss", "ss"]))
async def gwebss_cmd(c: Client, message: Message):
    """Takes a screenshot of a website."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("Please provide a URL to screenshot.")

    url = args[1]
    if not url.startswith("http"):
        url = "https://" + url

    msg = await message.reply_text(
        "📸 Taking screenshot... This might take a few seconds."
    )

    # Using a free public screenshot generation API
    ss_url = f"https://image.thum.io/get/width/1920/crop/1080/{url}"

    # Send the photo
    try:
        reply = await message.reply_photo(
            photo=ss_url, caption=f"📸 Screenshot of {url}"
        )
        if isinstance(reply, types.Error):
            await c.editTextMessage(
                chat_id=message.chat_id,
                message_id=msg.id,
                text="Failed to capture screenshot. The URL might be invalid or unreachable.",
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
            text=f"Error taking screenshot: {str(e)}",
            parse_mode="html",
        )
