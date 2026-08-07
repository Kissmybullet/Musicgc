#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core._httpx import HttpxClient

__mod_name__ = "English"
__help__ = """
*✿ Eɴɢʟɪꜱʜ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /define <word> ➛ Get the dictionary definition of an English word.
"""


@Client.on_message(filters=Filter.command(["define", "dict"]))
async def english_cmd(c: Client, message: Message):
    """Gets dictionary definition."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("Please provide an English word to define.")

    word = args[1]
    msg = await message.reply_text(f"🔍 Looking up the dictionary for `{word}`...")

    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    client = HttpxClient()
    response = await client.make_request(api_url)
    await client.close()

    if not response or isinstance(response, dict) and "title" in response:
        return await c.editTextMessage(
            chat_id=message.chat_id,
            message_id=msg.id,
            text=f"Could not find a definition for `{word}`.",
            parse_mode="markdown",
        )

    if isinstance(response, list) and len(response) > 0:
        data = response[0]
        word_text = data.get("word", word)
        phonetics = data.get("phonetic", "")

        text = f"📖 **Dictionary: {word_text.title()}**\n"
        if phonetics:
            text += f"*{phonetics}*\n"

        meanings = data.get("meanings", [])
        for meaning in meanings[:2]:  # Get max 2 parts of speech to save space
            pos = meaning.get("partOfSpeech", "unknown")
            text += f"\n**{pos.title()}**:\n"
            defs = meaning.get("definitions", [])
            for i, definition in enumerate(defs[:2], 1):  # Max 2 defs per pos
                text += f" {i}. {definition['definition']}\n"

        await c.editTextMessage(
            chat_id=message.chat_id, message_id=msg.id, text=text, parse_mode="markdown"
        )
