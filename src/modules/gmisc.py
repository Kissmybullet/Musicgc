#  Ported from LadyRezebb-reference/MukeshRobot/modules/misc.py
#  Miscellaneous commands: echo, markdownhelp

import html

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Misc"
__help__ = """
<b>Miscellaneous Commands:</b>
/echo &lt;text&gt; - Echo the text back
/markdownhelp - Show markdown formatting help
"""


MARKDOWN_HELP = """<b>Markdown Formatting Help</b>

Telegram supports the following formatting:

<i>Italics:</i> Wrap text with <code>_</code>
Example: <code>_italic_</code>

<b>Bold:</b> Wrap text with <code>*</code>
Example: <code>*bold*</code>

<code>Monospace:</code> Wrap text with <code>`</code>
Example: <code>`code`</code>

<u>Underline:</u> Wrap text with <code>__</code>
Example: <code>__underline__</code>

<s>Strikethrough:</s> Wrap text with <code>~</code>
Example: <code>~strikethrough~</code>

<tg-spoiler>Spoiler:</tg-spoiler> Wrap text with <code>||</code>
Example: <code>||spoiler||</code>

<b>Combined:</b> You can combine them!
Example: <code>*_bold italic_*</code>

<b>Links:</b> <code>[text](url)</code>
Example: <code>[Google](https://google.com)</code>

<b>Note:</b> In groups, use /echo to send a formatted message.
"""


@Client.on_message(filters=Filter.command("echo"))
async def echo_cmd(c: Client, message: types.Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text("Usage: /echo &lt;text&gt;")
        return

    text = args[1]

    if message.reply_to_message_id:
        replied = await message.getRepliedMessage()
        if isinstance(replied, types.Error):
            await message.reply_text("Failed to get replied message.")
            return
        await c.sendTextMessage(
            chat_id=message.chat_id,
            text=text,
            reply_to_message_id=replied.id,
        )
    else:
        await c.sendTextMessage(
            chat_id=message.chat_id,
            text=text,
        )

    await c.deleteMessages(chat_id=message.chat_id, message_ids=[message.id])


@Client.on_message(filters=Filter.command("markdownhelp"))
async def markdownhelp_cmd(c: Client, message: types.Message):
    if message.chat_id > 0:
        bot_username = c.me.usernames.editable_username if c.me.usernames else "bot"
        keyboard = types.ReplyMarkupInlineKeyboard(
            rows=[
                [
                    types.InlineKeyboardButton(
                        text="Markdown Help",
                        type=types.InlineKeyboardButtonTypeUrl(
                            url=f"t.me/{bot_username}?start=markdownhelp"
                        ),
                    )
                ]
            ]
        )
        await message.reply_text(
            "Contact me in PM for markdown help.",
            reply_markup=keyboard,
        )
    else:
        await message.reply_text(MARKDOWN_HELP)
