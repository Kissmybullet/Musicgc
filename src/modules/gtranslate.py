#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import html

from gpytranslate import Translator
from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Translator"
__help__ = """
<b>Translation Commands:</b>

• <code>/tr [lang] [text]</code> — Translate text to target language
• <code>/tl [lang] [text]</code> — Translate text (alias)

<b>Language codes:</b>
<code>en</code> English, <code>hi</code> Hindi, <code>es</code> Spanish,
<code>fr</code> French, <code>de</code> German, <code>ja</code> Japanese,
<code>ko</code> Korean, <code>zh</code> Chinese, <code>ru</code> Russian,
<code>ar</code> Arabic, <code>pt</code> Portuguese, <code>it</code> Italian
"""

translator = Translator()


@Client.on_message(filters=Filter.command(["tr", "tl"]))
async def translate_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 2)

    if len(parts) < 3:
        reply = await message.reply_text(
            "ℹ️ Usage: <code>/tr [lang] [text]</code>\n"
            "Example: <code>/tr es hello world</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"translate_cmd error: {reply.message}")
        return

    target_lang = parts[1].strip().lower()
    query = parts[2].strip()

    try:
        result = await translator.translate(query, destlang=target_lang)
        translated = result.text if hasattr(result, "text") else str(result)

        reply = await message.reply_text(
            f"🌐 <b>Translation ({html.escape(target_lang)}):</b>\n\n"
            f"{html.escape(translated)}\n\n"
            f"<i>Original:</i> <code>{html.escape(query)}</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"translate_cmd error: {reply.message}")

    except Exception as e:
        reply = await message.reply_text(
            f"❌ Translation error: <code>{html.escape(str(e))}</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"translate_cmd error: {reply.message}")
