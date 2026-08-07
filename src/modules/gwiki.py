#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import html

import wikipedia
from pytdbot import Client, types

from src.core import Filter

wikipedia.set_user_agent("MelodyForgeBot/1.0 (https://github.com/TheMukeshDev/MelodyForgeBot)")

__mod_name__ = "Wikipedia"
__help__ = """
<b>Wikipedia Commands:</b>

• <code>/wiki [query]</code> — Search Wikipedia for a summary
"""


@Client.on_message(filters=Filter.command("wiki"))
async def wiki_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text(
            "ℹ️ Please provide a search query.\nUsage: <code>/wiki [query]</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"wiki_cmd error: {reply.message}")
        return

    query = parts[1].strip()

    try:
        result = wikipedia.summary(query, sentences=3)
        page = wikipedia.page(query, auto_suggest=False)

        text_out = (
            f"<b>📖 Wikipedia: {html.escape(page.title)}</b>\n\n"
            f"{html.escape(result)}\n\n"
            f'🔗 <a href="{page.url}">Read more on Wikipedia</a>'
        )

        reply = await message.reply_text(text_out, disable_web_page_preview=True)
        if isinstance(reply, types.Error):
            c.logger.warning(f"wiki_cmd error: {reply.message}")

    except wikipedia.DisambiguationError as e:
        options = ", ".join(e.options[:5])
        reply = await message.reply_text(
            f"🔍 Multiple results found. Did you mean:\n<code>{html.escape(options)}</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"wiki_cmd error: {reply.message}")

    except wikipedia.PageError:
        reply = await message.reply_text(
            f"❌ No Wikipedia article found for <b>{html.escape(query)}</b>."
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"wiki_cmd error: {reply.message}")

    except Exception as e:
        reply = await message.reply_text(
            f"❌ Error searching Wikipedia: <code>{html.escape(str(e))}</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"wiki_cmd error: {reply.message}")
