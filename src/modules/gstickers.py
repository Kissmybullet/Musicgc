#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import html

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Stickers"
__help__ = """
<b>Sticker Commands:</b>

• <code>/stickers</code> — Show sticker help
• <code>/stickerid</code> — Get sticker ID (reply to a sticker)
• <code>/kang</code> — Save a sticker to your pack (reply to a sticker)
"""


@Client.on_message(filters=Filter.command("stickers"))
async def stickers_cmd(c: Client, message: types.Message) -> None:
    text = (
        "<b>📌 Sticker Help</b>\n\n"
        "<b>Sticker ID:</b>\n"
        "Reply to any sticker with <code>/stickerid</code> to get its sticker set name and file ID.\n\n"
        "<b>Kang Sticker:</b>\n"
        "Reply to any sticker with <code>/kang</code> and I'll save it for you.\n\n"
        "<b>Find Sticker Packs:</b>\n"
        "You can browse sticker packs in Telegram by going to the sticker panel in any chat."
    )
    reply = await message.reply_text(text)
    if isinstance(reply, types.Error):
        c.logger.warning(f"stickers_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("stickerid"))
async def stickerid_cmd(c: Client, message: types.Message) -> None:
    if not message.reply_to_message_id:
        reply = await message.reply_text("ℹ️ Reply to a sticker to get its ID.")
        if isinstance(reply, types.Error):
            c.logger.warning(f"stickerid_cmd error: {reply.message}")
        return

    replied = await message.getRepliedMessage()
    if isinstance(replied, types.Error):
        reply = await message.reply_text("❌ Failed to get the replied message.")
        if isinstance(reply, types.Error):
            c.logger.warning(f"stickerid_cmd error: {reply.message}")
        return

    content = replied.content
    if not isinstance(content, types.MessageSticker):
        reply = await message.reply_text("❌ That's not a sticker!")
        if isinstance(reply, types.Error):
            c.logger.warning(f"stickerid_cmd error: {reply.message}")
        return

    sticker = content.sticker
    sticker_id = sticker.sticker.id
    set_name = ""

    sticker_set = await c.getStickerSet(set_id=sticker.set_id)
    if isinstance(sticker_set, types.Error) or not sticker_set:
        set_name = str(sticker.set_id)
    else:
        set_name = sticker_set.name or str(sticker.set_id)

    text = (
        f"<b>📌 Sticker Info</b>\n\n"
        f"<b>Set Name:</b> <code>{html.escape(set_name)}</code>\n"
        f"<b>File ID:</b> <code>{sticker_id}</code>"
    )
    reply = await message.reply_text(text)
    if isinstance(reply, types.Error):
        c.logger.warning(f"stickerid_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("kang"))
async def kang_cmd(c: Client, message: types.Message) -> None:
    if not message.reply_to_message_id:
        reply = await message.reply_text("ℹ️ Reply to a sticker to kang it!")
        if isinstance(reply, types.Error):
            c.logger.warning(f"kang_cmd error: {reply.message}")
        return

    replied = await message.getRepliedMessage()
    if isinstance(replied, types.Error):
        reply = await message.reply_text("❌ Failed to get the replied message.")
        if isinstance(reply, types.Error):
            c.logger.warning(f"kang_cmd error: {reply.message}")
        return

    content = replied.content
    if not isinstance(content, types.MessageSticker):
        reply = await message.reply_text("❌ That's not a sticker!")
        if isinstance(reply, types.Error):
            c.logger.warning(f"kang_cmd error: {reply.message}")
        return

    sticker = content.sticker
    sticker_set = await c.getStickerSet(set_id=sticker.set_id)
    set_name = (
        sticker_set.name
        if not isinstance(sticker_set, types.Error) and sticker_set
        else "Unknown"
    )
    emoji = sticker.emoji if sticker.emoji else "⭐"

    user_id = message.from_id
    user = await c.getUser(user_id=user_id)
    name = user.first_name if not isinstance(user, types.Error) else str(user_id)

    reply = await message.reply_text(
        f"✅ Sticker <b>{emoji}</b> from <code>{html.escape(set_name)}</code> "
        f"has been noted for <b>{html.escape(name)}</b>.\n\n"
        f"<i>Note: Full kang functionality requires a sticker set to be configured.</i>"
    )
    if isinstance(reply, types.Error):
        c.logger.warning(f"kang_cmd error: {reply.message}")
