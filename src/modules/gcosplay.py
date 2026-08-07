import random

import aiohttp
from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Cosplay"
__help__ = """
<b>Cosplay Commands:</b>

• <code>/cosplay</code> — Get a random cosplay image
"""


COSPLAY_URLS = [
    "https://www.reddit.com/r/cosplay/hot.json",
    "https://www.reddit.com/r/cosplayers/hot.json",
    "https://www.reddit.com/r/animecosplay/hot.json",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TelegramBot/1.0)"}


@Client.on_message(filters=Filter.command("cosplay"))
async def cosplay_cmd(c: Client, message: types.Message) -> None:
    msg = await message.reply_text("Fetching cosplay image...")
    if isinstance(msg, types.Error):
        return

    try:
        sub_url = random.choice(COSPLAY_URLS)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                sub_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    raise Exception("Reddit API error")
                data = await resp.json()

        posts = data.get("data", {}).get("children", [])
        image_posts = []
        for p in posts:
            d = p.get("data", {})
            url = d.get("url", "")
            if any(
                url.endswith(ext) for ext in [".jpg", ".png", ".jpeg", ".gif", ".webp"]
            ):
                image_posts.append(d)
            elif d.get("post_hint") == "image" or "i.redd.it" in url:
                image_posts.append(d)

        if not image_posts:
            await msg.edit_text("No cosplay images found. Try again later.")
            return

        post = random.choice(image_posts)
        title = post.get("title", "Cosplay")
        url = post.get("url", "")
        author = post.get("author", "Unknown")
        score = post.get("score", 0)

        result = f"<b>{title}</b>\nAuthor: u/{author}\nScore: {score}"

        reply = await msg.edit_text(result)
        if isinstance(reply, types.Error):
            return

        if url:
            await message.reply_photo(url, caption=f"{title}")

    except Exception:
        await msg.edit_text("Failed to fetch cosplay image. Try again later.")
