import html

import aiohttp
from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Urban Dictionary"
__help__ = """
<b>Urban Dictionary Commands:</b>

• <code>/ud [word]</code> — Search Urban Dictionary
"""


@Client.on_message(filters=Filter.command("ud"))
async def ud_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text("Usage: <code>/ud [word]</code>")
        if isinstance(reply, types.Error):
            c.logger.warning(f"ud_cmd error: {reply.message}")
        return

    query = parts[1].strip()
    msg = await message.reply_text(
        f"🔍 Searching Urban Dictionary for <b>{html.escape(query)}</b>..."
    )
    if isinstance(msg, types.Error):
        return

    try:
        url = f"https://api.urbandictionary.com/v0/define?term={query}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    await msg.edit_text(
                        "❌ Failed to fetch results from Urban Dictionary."
                    )
                    return
                data = await resp.json()

        entries = data.get("list", [])
        if not entries:
            await msg.edit_text(f"❌ No results found for <b>{html.escape(query)}</b>.")
            return

        entry = entries[0]
        definition = entry.get("definition", "N/A")
        example = entry.get("example", "N/A")
        author = entry.get("author", "Unknown")
        thumbs_up = entry.get("thumbs_up", 0)
        thumbs_down = entry.get("thumbs_down", 0)

        if len(definition) > 800:
            definition = definition[:800] + "..."
        if len(example) > 400:
            example = example[:400] + "..."

        result = (
            f"📖 <b>{html.escape(entry.get('word', query))}</b>\n\n"
            f"<b>Definition:</b>\n{html.escape(definition)}\n\n"
            f"<b>Example:</b>\n<i>{html.escape(example)}</i>\n\n"
            f"👍 <code>{thumbs_up}</code> | 👎 <code>{thumbs_down}</code>\n"
            f"<i>By: {html.escape(author)}</i>"
        )

        await msg.edit_text(result, disable_web_page_preview=True)

    except Exception as e:
        await msg.edit_text(f"❌ Error: <code>{html.escape(str(e))}</code>")
