#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core._httpx import HttpxClient
import urllib.parse

__mod_name__ = "ChatGPT"
__help__ = """
*✿ CʜᴀᴛGPT ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /gpt <prompt> ➛ Ask ChatGPT a question or give it a prompt.
"""


@Client.on_message(filters=Filter.command(["gpt", "chatgpt"]))
async def gchatgpt_cmd(c: Client, message: Message):
    """Ask ChatGPT."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("Please provide a prompt for ChatGPT.")

    prompt = args[1]
    msg = await message.reply_text("Thinking...")
    from pytdbot.types import ChatActionTyping
    await c.sendChatAction(chat_id=message.chat_id, action=ChatActionTyping())

    encoded_prompt = urllib.parse.quote(prompt)
    api_url = f"https://api.safone.dev/chatgpt?query={encoded_prompt}"

    try:
        client = HttpxClient()
        response = await client.make_request(api_url)
        await client.close()

        if response and "message" in response:
            reply_text = response["message"]
            await c.editTextMessage(
                chat_id=message.chat_id,
                message_id=msg.id,
                text=reply_text,
                parse_mode="html",
            )
        else:
            # Try fallback free API if safone is down
            fallback_url = (
                f"https://chatgpt.apinepdev.workers.dev/?question={encoded_prompt}"
            )
            client2 = HttpxClient()
            response2 = await client2.make_request(fallback_url)
            await client2.close()

            if response2 and "answer" in response2:
                await c.editTextMessage(
                    chat_id=message.chat_id,
                    message_id=msg.id,
                    text=response2["answer"],
                    parse_mode="html",
                )
            else:
                await c.editTextMessage(
                    chat_id=message.chat_id,
                    message_id=msg.id,
                    text="Sorry, the AI is currently overloaded. Please try again later.",
                    parse_mode="html",
                )
    except Exception:
        await c.editTextMessage(
            chat_id=message.chat_id,
            message_id=msg.id,
            text="Sorry, the AI is currently overloaded or the API is down. Please try again later.",
            parse_mode="html",
        )
