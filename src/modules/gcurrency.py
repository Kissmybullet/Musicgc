#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core._httpx import HttpxClient

__mod_name__ = "Currency"
__help__ = """
*✿ Cᴜʀʀᴇɴᴄʏ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /cash <amount> <from> <to> ➛ Convert currency. Example: /cash 100 USD INR
"""


@Client.on_message(filters=Filter.command(["cash", "currency"]))
async def currency_cmd(c: Client, message: Message):
    """Converts currency."""
    args = message.text.split()
    if len(args) < 4:
        return await message.reply_text(
            "Invalid syntax! Usage: `/cash <amount> <from> <to>`\nExample: `/cash 10 USD INR`",
            parse_mode="markdown",
        )

    try:
        amount = float(args[1])
    except ValueError:
        return await message.reply_text("Please provide a valid amount (number).")

    base = args[2].upper()
    target = args[3].upper()

    msg = await message.reply_text("💱 Fetching live conversion rates...")

    api_url = f"https://api.exchangerate-api.com/v4/latest/{base}"
    client = HttpxClient()
    data = await client.make_request(api_url)
    await client.close()

    if not data or "rates" not in data:
        return await c.editTextMessage(
            chat_id=message.chat_id,
            message_id=msg.id,
            text=f"Failed to fetch conversion rates. Please check if `{base}` is a valid currency code.",
            parse_mode="markdown",
        )

    if target not in data["rates"]:
        return await c.editTextMessage(
            chat_id=message.chat_id,
            message_id=msg.id,
            text=f"Invalid target currency code: `{target}`.",
            parse_mode="markdown",
        )

    rate = data["rates"][target]
    result = amount * rate

    text = (
        f"**💱 Live Currency Conversion:**\n\n"
        f"**Amount:** `{amount} {base}`\n"
        f"**Converted:** `{round(result, 2)} {target}`\n"
        f"**Rate:** `1 {base} = {rate} {target}`"
    )

    await c.editTextMessage(
        chat_id=message.chat_id, message_id=msg.id, text=text, parse_mode="markdown"
    )
