#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core._httpx import HttpxClient
import urllib.parse

__mod_name__ = "URL Shortener"
__help__ = """
*✿ URL Sʜᴏʀᴛᴇɴᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /short <url> ➛ Shortens the given URL using is.gd.
"""


@Client.on_message(filters=Filter.command(["short", "shorten"]))
async def gurlshortener_cmd(c: Client, message: Message):
    """Shortens links."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("Please provide a URL to shorten.")

    url = args[1]
    if not url.startswith("http"):
        url = "https://" + url

    encoded_url = urllib.parse.quote(url)
    api_url = f"https://is.gd/create.php?format=json&url={encoded_url}"

    msg = await message.reply_text("Shortening URL...")

    client = HttpxClient()
    response = await client.make_request(api_url)
    await client.close()

    if response and "shorturl" in response:
        short_url = response["shorturl"]
        await c.editTextMessage(
            chat_id=message.chat_id,
            message_id=msg.id,
            text=f"🔗 **Original URL:** {url}\n✨ **Shortened URL:** `{short_url}`",
            parse_mode="markdown",
            disable_web_page_preview=True,
        )
    else:
        error = (
            response.get("errormessage", "Unknown error")
            if response
            else "Failed to connect to API"
        )
        await c.editTextMessage(
            chat_id=message.chat_id,
            message_id=msg.id,
            text=f"Failed to shorten URL: {error}",
            parse_mode="html",
        )
