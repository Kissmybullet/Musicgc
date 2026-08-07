import html

import aiohttp
from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Time"
__help__ = """
<b>Time Commands:</b>

• <code>/time [timezone]</code> — Get current time
• <code>/date [timezone]</code> — Get current date
"""


async def _fetch_time(timezone: str) -> dict | None:
    url = f"https://worldtimeapi.org/api/timezone/{timezone}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                return await resp.json()
    return None


@Client.on_message(filters=Filter.command("time"))
async def time_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text(
            "Usage: <code>/time [timezone]</code>\nExample: <code>/time Asia/Kolkata</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"time_cmd error: {reply.message}")
        return

    tz = parts[1].strip()
    msg = await message.reply_text(f"🕐 Fetching time for <b>{html.escape(tz)}</b>...")
    if isinstance(msg, types.Error):
        return

    data = await _fetch_time(tz)
    if not data:
        await msg.edit_text(
            f"❌ Invalid timezone or API error.\nTry: <code>Asia/Kolkata</code>, <code>US/Eastern</code>, etc."
        )
        return

    datetime_str = data.get("datetime", "N/A")
    time_str = datetime_str[11:19] if len(datetime_str) > 19 else datetime_str
    utc_offset = data.get("utc_offset", "N/A")

    await msg.edit_text(
        f"🕐 <b>Time in {html.escape(tz)}:</b>\n"
        f"<code>{time_str}</code>\n"
        f"<b>UTC Offset:</b> <code>{utc_offset}</code>"
    )


@Client.on_message(filters=Filter.command("date"))
async def date_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text(
            "Usage: <code>/date [timezone]</code>\nExample: <code>/date Europe/London</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"date_cmd error: {reply.message}")
        return

    tz = parts[1].strip()
    msg = await message.reply_text(f"📅 Fetching date for <b>{html.escape(tz)}</b>...")
    if isinstance(msg, types.Error):
        return

    data = await _fetch_time(tz)
    if not data:
        await msg.edit_text(
            f"❌ Invalid timezone or API error.\nTry: <code>Asia/Kolkata</code>, <code>US/Eastern</code>, etc."
        )
        return

    datetime_str = data.get("datetime", "N/A")
    date_str = datetime_str[:10] if len(datetime_str) >= 10 else datetime_str
    day_of_week = data.get("day_of_week", "N/A")
    day_of_year = data.get("day_of_year", "N/A")
    week_number = data.get("week_number", "N/A")

    await msg.edit_text(
        f"📅 <b>Date in {html.escape(tz)}:</b>\n"
        f"<code>{date_str}</code>\n"
        f"<b>Day:</b> <code>{day_of_week}</code>\n"
        f"<b>Day of Year:</b> <code>{day_of_year}</code>\n"
        f"<b>Week Number:</b> <code>{week_number}</code>"
    )
