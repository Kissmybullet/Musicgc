import html

import aiohttp
from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Paste"
__help__ = """
<b>Paste Commands:</b>

• <code>/paste [text]</code> — Paste text to dpaste.org
"""


@Client.on_message(filters=Filter.command("paste"))
async def paste_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)

    paste_text = ""
    if message.reply_to_message_id:
        replied = await message.getRepliedMessage()
        if not isinstance(replied, types.Error) and hasattr(replied, "text"):
            paste_text = replied.text.text if hasattr(replied.text, "text") else ""
    elif len(parts) > 1:
        paste_text = parts[1]

    if not paste_text.strip():
        reply = await message.reply_text(
            "Usage: <code>/paste [text]</code> or reply to a message with <code>/paste</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"paste_cmd error: {reply.message}")
        return

    msg = await message.reply_text("Pasting...")
    if isinstance(msg, types.Error):
        return

    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field("content", paste_text)
            data.add_field("syntax", "python")

            async with session.post(
                "https://dpaste.org/api/",
                data=data,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    await msg.edit_text(f"Paste failed with status {resp.status}.")
                    return
                result = await resp.text()

        result = result.strip()
        paste_url = result.replace("dpaste.org/", "dpaste.org/show/")

        await msg.edit_text(
            f'Pasted successfully!\n\n<a href="{paste_url}">View Paste</a>',
            disable_web_page_preview=True,
        )

    except Exception as e:
        await msg.edit_text(f"Paste failed: <code>{html.escape(str(e))}</code>")
