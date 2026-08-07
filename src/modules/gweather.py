#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import asyncio
import html

import aiohttp
from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Weather"
__help__ = """
<b>Weather Commands:</b>

• <code>/weather [city]</code> — Get weather info for a city
"""


@Client.on_message(filters=Filter.command("weather"))
async def weather_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text(
            "ℹ️ Please provide a city name.\nUsage: <code>/weather [city]</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"weather_cmd error: {reply.message}")
        return

    city = parts[1].strip()

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://wttr.in/{city}?format=3"
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    result = await resp.text()
                    reply = await message.reply_text(
                        f"🌤 <b>Weather:</b>\n<code>{html.escape(result.strip())}</code>"
                    )
                else:
                    reply = await message.reply_text(
                        f"❌ Could not find weather for <b>{html.escape(city)}</b>."
                    )
                if isinstance(reply, types.Error):
                    c.logger.warning(f"weather_cmd error: {reply.message}")
    except asyncio.TimeoutError:
        reply = await message.reply_text("⏱️ Request timed out. Please try again.")
        if isinstance(reply, types.Error):
            c.logger.warning(f"weather_cmd error: {reply.message}")
    except Exception as e:
        reply = await message.reply_text(
            f"❌ Error fetching weather: <code>{html.escape(str(e))}</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"weather_cmd error: {reply.message}")
