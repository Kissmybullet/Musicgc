import html

import aiohttp
from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Sports"
__help__ = """
<b>Sports Commands:</b>

• <code>/cricket</code> — Get latest cricket scores
• <code>/football</code> — Get latest football scores
"""


async def _fetch_json(url: str) -> dict | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception:
        pass
    return None


@Client.on_message(filters=Filter.command("cricket"))
async def cricket_cmd(c: Client, message: types.Message) -> None:
    msg = await message.reply_text("🏏 Fetching cricket scores...")
    if isinstance(msg, types.Error):
        return

    try:
        data = await _fetch_json("https://crickbuzz.p.rapidapi.com/recent-matches")
        if not data:
            await msg.edit_text(
                "🏏 <b>Cricket scores service coming soon!</b>\n\nStay tuned for live cricket updates."
            )
            return

        matches = data.get("matches", [])
        if not matches:
            await msg.edit_text("❌ No recent cricket matches found.")
            return

        text = "🏏 <b>Recent Cricket Matches</b>\n\n"
        for match in matches[:5]:
            team1 = match.get("team1", {}).get("name", "TBD")
            team2 = match.get("team2", {}).get("name", "TBD")
            status = match.get("status", "N/A")
            text += f"<b>{html.escape(team1)}</b> vs <b>{html.escape(team2)}</b>\n"
            text += f"<i>{html.escape(status)}</i>\n\n"

        await msg.edit_text(text)

    except Exception:
        await msg.edit_text(
            "🏏 <b>Cricket scores service coming soon!</b>\n\nStay tuned for live cricket updates."
        )


@Client.on_message(filters=Filter.command("football"))
async def football_cmd(c: Client, message: types.Message) -> None:
    msg = await message.reply_text("⚽ Fetching football scores...")
    if isinstance(msg, types.Error):
        return

    try:
        data = await _fetch_json(
            "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d=2026-01-01"
        )
        if not data or not data.get("events"):
            await msg.edit_text(
                "⚽ <b>Football scores service coming soon!</b>\n\nStay tuned for live football updates."
            )
            return

        events = data["events"][:5]
        text = "⚽ <b>Football Events</b>\n\n"
        for event in events:
            home = event.get("strEvent", "TBD")
            league = event.get("strLeague", "N/A")
            text += f"<b>{html.escape(home)}</b>\n"
            text += f"<i>{html.escape(league)}</i>\n\n"

        await msg.edit_text(text)

    except Exception:
        await msg.edit_text(
            "⚽ <b>Football scores service coming soon!</b>\n\nStay tuned for live football updates."
        )
