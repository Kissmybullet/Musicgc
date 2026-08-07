#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import asyncio
from platform import python_version as pyver

from pytdbot import Client, types

from src import __version__
from src.core import Filter, config

__mod_name__ = "Alive"
__help__ = """
<b>Alive Commands:</b>
• <code>/alive</code> — Check if the bot is alive and see its stats
"""


@Client.on_message(filters=Filter.command("alive"))
async def alive_cmd(c: Client, message: types.Message):
    """Handles the /alive command to show the bot is alive."""
    chat_id = message.chat_id

    # Delete the command message
    await c.deleteMessages(chat_id=chat_id, message_ids=[message.id], revoke=True)

    # Send a waiting message
    reply = await message.reply_text("⚡")
    if isinstance(reply, types.Error):
        return

    await asyncio.sleep(0.2)
    await reply.edit_text("ᴅɪɴɢ ᴅᴏɴɢ ꨄ︎ ᴀʟɪᴠɪɴɢ..")
    await asyncio.sleep(0.1)
    await reply.edit_text("ᴅɪɴɢ ᴅᴏɴɢ ꨄ︎ ᴀʟɪᴠɪɴɢ......")
    await asyncio.sleep(0.1)
    await reply.edit_text("ᴅɪɴɢ ᴅᴏɴɢ ꨄ︎ ᴀʟɪᴠɪɴɢ..")
    await c.deleteMessages(chat_id=chat_id, message_ids=[reply.id], revoke=True)
    await asyncio.sleep(0.3)

    # Try sending sticker
    sticker_msg = await c.sendSticker(
        chat_id=chat_id,
        sticker=types.InputFileRemote(
            id="CAACAgUAAxkDAAJHbmLuy2NEfrfh6lZSohacEGrVjd5wAAIOBAACl42QVKnra4sdzC_uKQQ"
        ),
        reply_to_message_id=message.id,
    )
    if not isinstance(sticker_msg, types.Error):
        await c.deleteMessages(
            chat_id=chat_id, message_ids=[sticker_msg.id], revoke=True
        )

    await asyncio.sleep(0.2)

    owner_id = config.OWNER_ID if config.OWNER_ID else "Unknown"
    bot_name = c.me.first_name
    bot_username = c.me.usernames.editable_username

    caption = f"""**ʜᴇʏ, ɪ ᴀᴍ 『[{bot_name}](https://t.me/{bot_username})』**
━━━━━━━━━━━━━━━━━━━
» **ᴍʏ ᴏᴡɴᴇʀ :** [ᴏᴡɴᴇʀ](tg://user?id={owner_id})
  
» **ʙᴏᴛ ᴠᴇʀsɪᴏɴ :** `{__version__}`
  
» **ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ :** `{pyver()}`
━━━━━━━━━━━━━━━━━━━"""

    markup = types.ReplyMarkupInlineKeyboard(
        rows=[
            [
                types.InlineKeyboardButton(
                    text="ɴᴏᴏʙ",
                    type=types.InlineKeyboardButtonTypeUrl(
                        url=f"tg://user?id={owner_id}"
                    ),
                ),
                types.InlineKeyboardButton(
                    text="ꜱᴜᴘᴘᴏʀᴛ",
                    type=types.InlineKeyboardButtonTypeUrl(url=config.SUPPORT_GROUP),
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="➕ᴀᴅᴅ ᴍᴇ ᴇʟsᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ➕",
                    type=types.InlineKeyboardButtonTypeUrl(
                        url=f"https://t.me/{bot_username}?startgroup=true"
                    ),
                ),
            ],
        ]
    )

    await c.sendPhoto(
        chat_id=chat_id,
        photo=types.InputFileRemote(id=config.START_IMG),
        caption=caption,
        parse_mode="html",
        reply_to_message_id=message.id,
        reply_markup=markup,
    )
