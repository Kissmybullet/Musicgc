import html
from urllib.parse import quote_plus

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Google"
__help__ = """
<b>Google Commands:</b>

• <code>/google [query]</code> — Search Google
"""


@Client.on_message(filters=Filter.command("google"))
async def google_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text("Usage: <code>/google [query]</code>")
        if isinstance(reply, types.Error):
            c.logger.warning(f"google_cmd error: {reply.message}")
        return

    query = parts[1].strip()

    try:
        from search_engine_parser.core.engines.google import SearchEngine

        search = SearchEngine()
        results = await search.search(query, page=1)

        if not results:
            raise Exception("No results")

        output = f"🔍 <b>Google Search: {html.escape(query)}</b>\n\n"
        for i, r in enumerate(results[:5], 1):
            title = r.get("titles", "N/A")
            link = r.get("links", "")
            snippet = r.get("descriptions", "No description")
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            output += f"<b>{i}. {html.escape(title)}</b>\n"
            output += f"   <code>{html.escape(snippet)}</code>\n"
            if link:
                output += f'   <a href="{link}">Link</a>\n'
            output += "\n"

        reply = await message.reply_text(output, disable_web_page_preview=True)
        if isinstance(reply, types.Error):
            c.logger.warning(f"google_cmd error: {reply.message}")

    except ImportError:
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        reply = await message.reply_text(
            f"🔍 <b>Google Search</b>\n\n"
            f'Click here to search: <a href="{search_url}">{html.escape(query)}</a>',
            disable_web_page_preview=False,
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"google_cmd error: {reply.message}")
    except Exception as e:
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        reply = await message.reply_text(
            f"🔍 <b>Google Search</b>\n\n"
            f'Click here to search: <a href="{search_url}">{html.escape(query)}</a>\n'
            f"<i>Error: {html.escape(str(e))}</i>",
            disable_web_page_preview=False,
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"google_cmd error: {reply.message}")
