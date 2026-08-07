from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Instagram"
__help__ = """
<b>Instagram Commands:</b>

• <code>/insta [url]</code> — Download Instagram media
"""


@Client.on_message(filters=Filter.command("insta"))
async def insta_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text(
            "Usage: <code>/insta [instagram_url]</code>\n"
            "Example: <code>/insta https://www.instagram.com/p/ABC123/</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"insta_cmd error: {reply.message}")
        return

    url = parts[1].strip()
    if "instagram.com" not in url and "instagr.am" not in url:
        reply = await message.reply_text("❌ Please provide a valid Instagram URL.")
        if isinstance(reply, types.Error):
            c.logger.warning(f"insta_cmd error: {reply.message}")
        return

    reply = await message.reply_text(
        "📥 Instagram downloading is not directly supported via API.\n\n"
        "Please use one of these services:\n"
        '• <a href="https://snapinsta.app">SnapInsta</a>\n'
        '• <a href="https://saveig.app">SaveIG</a>\n'
        '• <a href="https://igram.io">iGram</a>\n\n'
        f"🔗 Your link: {url}",
        disable_web_page_preview=True,
    )
    if isinstance(reply, types.Error):
        c.logger.warning(f"insta_cmd error: {reply.message}")
