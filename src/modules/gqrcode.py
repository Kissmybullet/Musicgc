#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import html
import urllib.parse

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "QR Code"
__help__ = """
<b>QR Code Commands:</b>

• <code>/qrcode [text/url]</code> — Generate a QR code image
"""


@Client.on_message(filters=Filter.command("qrcode"))
async def qrcode_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text(
            "ℹ️ Please provide text or a URL to encode.\n"
            "Usage: <code>/qrcode [text or URL]</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"qrcode_cmd error: {reply.message}")
        return

    data = parts[1].strip()
    encoded_data = urllib.parse.quote(data, safe="")
    qr_url = (
        f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_data}"
    )

    reply = await message.reply_text(
        f"📱 <b>QR Code for:</b>\n<code>{html.escape(data)}</code>\n\n"
        f'🔗 <a href="{qr_url}">Click here to view QR Code</a>'
    )
    if isinstance(reply, types.Error):
        c.logger.warning(f"qrcode_cmd error: {reply.message}")
