import html

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Whois"
__help__ = """
<b>Whois Commands:</b>

• <code>/whois [username]</code> — Get info about a Telegram user
"""


@Client.on_message(filters=Filter.command("whois"))
async def whois_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text("Usage: <code>/whois [username]</code>")
        if isinstance(reply, types.Error):
            c.logger.warning(f"whois_cmd error: {reply.message}")
        return

    username = parts[1].strip().lstrip("@")
    msg = await message.reply_text("🔍 Searching...")
    if isinstance(msg, types.Error):
        return

    try:
        result = await c.searchPublicChat(username=username)
        if isinstance(result, types.Error):
            await msg.edit_text(f"❌ Error: <code>{html.escape(result.message)}</code>")
            return

        info = f"<b>Username:</b> @{username}\n"
        info += f"<b>Name:</b> {html.escape(result.title or 'N/A')}\n"

        if hasattr(result, "type"):
            import json
            try:
                type_dict = json.loads(str(result.type))
                chat_type = type_dict.get("@type", "Unknown").replace("chatType", "")
            except Exception:
                chat_type = "Unknown"
            info += f"<b>Type:</b> {chat_type}\n"

        if hasattr(result, "description") and result.description:
            desc = (
                result.description.text
                if hasattr(result.description, "text")
                else str(result.description)
            )
            if len(desc) > 500:
                desc = desc[:500] + "..."
            info += f"<b>Description:</b>\n{html.escape(desc)}\n"

        if hasattr(result, "photo") and result.photo:
            info += "<b>Has Profile Photo:</b> ✅\n"

        await msg.edit_text(info, disable_web_page_preview=True)
    except Exception as e:
        await msg.edit_text(f"❌ Error: <code>{html.escape(str(e))}</code>")
