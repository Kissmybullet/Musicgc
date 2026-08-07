#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import html
import random

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Anime"
__help__ = """
<b>Anime Commands:</b>

• <code>/anime [title]</code> — Search for an anime on MyAnimeList
• <code>/animequotes</code> — Get a random anime quote
• <code>/quote</code> — Get a random anime quote
"""

ANIME_QUOTES = [
    '"In order to exceed someone, you need to be aware of your own weakness." — Levi, Attack on Titan',
    "\"The world isn't perfect. But it's there for us, doing the best it can.\" — Kiritsugu, Fate/Zero",
    "\"If you don't take risks, you can't create a future.\" — Monkey D. Luffy, One Piece",
    "\"People's lives don't end when they die. It ends when they lose faith.\" — Erwin, Attack on Titan",
    "\"I'll leave tomorrow's problems to tomorrow's me.\" — Saitama, One Punch Man",
    '"The only thing we can do is live our lives to the fullest." — Naruto, Naruto Shippuden',
    '"The world is cruel, but also very beautiful." — Mikasa, Attack on Titan',
    '"Giving up is what kills people." — Hange, Attack on Titan',
    '"To know sorrow is to know humanity. It\'s what connects people." — Jiraiya, Naruto',
    '"No matter how hard or impossible it is, never lose sight of your goal." — Luffy, One Piece',
    '"A lesson without pain is meaningless." — Roy Mustang, Fullmetal Alchemist',
    '"Even if it\'s painful, you have to keep moving forward." — Soma, Food Wars',
    "\"If you can't do something, then don't. Focus on what you can do.\" — Shiro, No Game No Life",
    '"The ticket to the future is always open." — Suzaku, Code Geass',
    '"If nobody comes to save you, then you have to save yourself." — Guts, Berserk',
    '"I am afraid that the more I get used to this world, the less I will value my own." — Alphonse, FMA',
    '"Knowing what you can and can\'t do is part of growing up." — Lelouch, Code Geass',
    '"A man who has nothing to protect has nothing to lose." — Asta, Black Clover',
    "\"Just because you're trash doesn't mean you can't do great things.\" — Oreki, Hyouka",
    '"The loneliest people are the kindest." — Itachi, Naruto',
]


@Client.on_message(filters=Filter.command("anime"))
async def anime_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text(
            "ℹ️ Please provide an anime title to search.\n"
            "Usage: <code>/anime [title]</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"anime_cmd error: {reply.message}")
        return

    query = parts[1].strip()

    reply = await message.reply_text(f"🔍 Searching for <b>{html.escape(query)}</b>...")
    if isinstance(reply, types.Error):
        c.logger.warning(f"anime_cmd error: {reply.message}")
        return

    try:
        from jikanpy import AioJikan

        jikan = AioJikan()
        result = await jikan.searchanime(query)

        if not result.get("data"):
            await reply.edit_text(f"❌ No anime found for <b>{html.escape(query)}</b>.")
            return

        anime = result["data"][0]
        title = anime.get("title", "Unknown")
        title_jp = anime.get("title_japanese", "")
        episodes = anime.get("episodes", "N/A")
        status = anime.get("status", "Unknown")
        score = anime.get("score", "N/A")
        synopsis = anime.get("synopsis", "No synopsis available.")
        url = anime.get("url", "")

        if len(synopsis) > 500:
            synopsis = synopsis[:500] + "..."

        anime_text = f"<b>🎬 {html.escape(title)}</b>\n"
        if title_jp:
            anime_text += f"<i>({html.escape(title_jp)})</i>\n"
        anime_text += (
            f"\n"
            f"<b>📊 Score:</b> <code>{score}</code>\n"
            f"<b>📺 Episodes:</b> <code>{episodes}</code>\n"
            f"<b>📌 Status:</b> <code>{html.escape(status)}</code>\n"
            f"\n"
            f"<b>📝 Synopsis:</b>\n{html.escape(synopsis)}\n"
        )
        if url:
            anime_text += f'\n🔗 <a href="{url}">View on MyAnimeList</a>'

        await reply.edit_text(anime_text, disable_web_page_preview=True)

    except ImportError:
        await reply.edit_text("❌ The <code>jikanpy</code> package is not installed.")
    except Exception as e:
        await reply.edit_text(
            f"❌ Error searching anime: <code>{html.escape(str(e))}</code>"
        )


@Client.on_message(filters=Filter.command(["animequotes", "quote"]))
async def animequote_cmd(c: Client, message: types.Message) -> None:
    quote = random.choice(ANIME_QUOTES)
    reply = await message.reply_text(f"🎌 <b>Anime Quote:</b>\n\n<i>{quote}</i>")
    if isinstance(reply, types.Error):
        c.logger.warning(f"animequote_cmd error: {reply.message}")
