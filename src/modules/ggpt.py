from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core._httpx import HttpxClient

__mod_name__ = "GPT"
__help__ = """
*✿ GPT ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

/chat, /ask, /gpt <prompt> - Ask GPT a question.
"""


@Client.on_message(filters=Filter.command(["chat", "ask","gpt"]))
async def gpt_cmd(c: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("Give me a query too...")

    prompt = args[1]
    msg = await message.reply_text("Thinking...")
    from pytdbot.types import ChatActionTyping
    await c.sendChatAction(chat_id=message.chat_id, action=ChatActionTyping())

    client = HttpxClient()
    try:
        response = await client.make_request(
            "https://lexica.qewertyy.me/models",
            method="POST",
            json={"model_id": 5, "prompt": prompt},
        )
        await client.close()

        if response and "content" in response:
            await c.editTextMessage(
                chat_id=message.chat_id,
                message_id=msg.id,
                text=response["content"],
                parse_mode="html",
            )
        else:
            await c.editTextMessage(
                chat_id=message.chat_id,
                message_id=msg.id,
                text="Currently API is Down!",
                parse_mode="html",
            )
    except Exception:
        await client.close()
        await c.editTextMessage(
            chat_id=message.chat_id,
            message_id=msg.id,
            text="Currently API is Down!",
            parse_mode="html",
        )
