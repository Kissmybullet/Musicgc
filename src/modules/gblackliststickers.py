#  Ported from LadyRezebb-reference/MukeshRobot/modules/blacklist_stickers.py
#  Blacklist stickers: auto-delete blacklisted sticker messages

import html

from pytdbot import Client, types

from src.core import Filter, group_db
from src.core._admins import is_admin, load_admin_cache
from src.modules._helpers import delete_message, get_chat_title

__mod_name__ = "BlacklistStickers"
__help__ = """
<b>Blacklist Sticker Commands:</b>
/blackliststicker - View current blacklisted stickers
/blackliststicker &lt;sticker_set&gt; - Add sticker set to blacklist (or reply to a sticker)
/unblackliststicker &lt;sticker_set&gt; - Remove sticker set from blacklist (or reply)
/blackliststickers - Alias for blackliststicker list

Blacklisted stickers are automatically deleted when sent.
"""


@Client.on_message(filters=Filter.command("blackliststickers"))
async def blackliststickers_list_cmd(c: Client, message: types.Message):
    await _list_blacklist_stickers(c, message)


@Client.on_message(filters=Filter.command("blackliststicker"))
async def blackliststicker_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split(None, 1)

    if len(args) < 2 and not message.reply_to_message_id:
        await _list_blacklist_stickers(c, message)
        return

    if message.reply_to_message_id:
        replied = await message.getRepliedMessage()
        if isinstance(replied, types.Error):
            await message.reply_text("Failed to get the replied message.")
            return

        content = replied.content
        if isinstance(content, types.MessageSticker):
            sticker = content.sticker
            sticker_set = await c.getStickerSet(set_id=sticker.set_id)
            set_name = (
                sticker_set.name
                if not isinstance(sticker_set, types.Error) and sticker_set
                else None
            )
            if not set_name:
                await message.reply_text("Sticker has no set name!")
                return
            set_name = set_name.lower()
            await group_db.add_blacklist_sticker(chat_id, set_name)
            await message.reply_text(
                f"Sticker set <code>{html.escape(set_name)}</code> "
                f"added to blacklist in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
            )
        else:
            await message.reply_text("Reply to a sticker to blacklist its set.")
        return

    text = args[1].strip()
    text = text.replace("https://t.me/addstickers/", "")
    to_blacklist = list({t.strip().lower() for t in text.split("\n") if t.strip()})

    added = 0
    for trigger in to_blacklist:
        await group_db.add_blacklist_sticker(chat_id, trigger)
        added += 1

    if added == 1:
        await message.reply_text(
            f"Sticker set <code>{html.escape(to_blacklist[0])}</code> "
            f"added to blacklist in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
        )
    elif added > 1:
        await message.reply_text(
            f"<b>{added}</b> sticker sets added to blacklist in "
            f"<b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
        )


@Client.on_message(filters=Filter.command("unblackliststicker"))
async def unblackliststicker_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split(None, 1)

    if message.reply_to_message_id:
        replied = await message.getRepliedMessage()
        if isinstance(replied, types.Error):
            await message.reply_text("Failed to get the replied message.")
            return

        content = replied.content
        if isinstance(content, types.MessageSticker):
            sticker = content.sticker
            sticker_set = await c.getStickerSet(set_id=sticker.set_id)
            set_name = (
                sticker_set.name
                if not isinstance(sticker_set, types.Error) and sticker_set
                else None
            )
            if not set_name:
                await message.reply_text("Sticker has no set name!")
                return
            set_name = set_name.lower()
            current = await group_db.get_blacklist_stickers(chat_id)
            if set_name in [s.lower() for s in current]:
                await group_db.rm_blacklist_sticker(chat_id, set_name)
                await message.reply_text(
                    f"Sticker set <code>{html.escape(set_name)}</code> "
                    f"removed from blacklist in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
                )
            else:
                await message.reply_text("That sticker set is not blacklisted.")
        else:
            await message.reply_text(
                "Reply to a sticker to remove its set from blacklist."
            )
        return

    if len(args) < 2:
        await message.reply_text(
            "Tell me which sticker set you want to remove from the blacklist."
        )
        return

    text = args[1].strip()
    text = text.replace("https://t.me/addstickers/", "")
    to_unblacklist = list({t.strip().lower() for t in text.split("\n") if t.strip()})

    current = await group_db.get_blacklist_stickers(chat_id)
    current_lower = [s.lower() for s in current]
    successful = 0

    for trigger in to_unblacklist:
        if trigger in current_lower:
            await group_db.rm_blacklist_sticker(chat_id, trigger)
            successful += 1

    if len(to_unblacklist) == 1:
        if successful:
            await message.reply_text(
                f"Sticker set <code>{html.escape(to_unblacklist[0])}</code> "
                f"removed from blacklist in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
            )
        else:
            await message.reply_text("That sticker set is not on the blacklist!")
    elif successful == len(to_unblacklist):
        await message.reply_text(
            f"Removed <b>{successful}</b> sticker sets from blacklist in "
            f"<b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
        )
    elif not successful:
        await message.reply_text("None of these sticker sets are blacklisted.")
    else:
        await message.reply_text(
            f"Removed <b>{successful}</b> sticker sets. "
            f"<b>{len(to_unblacklist) - successful}</b> did not exist."
        )


async def _list_blacklist_stickers(c: Client, message: types.Message):
    chat_id = message.chat_id
    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    stickers = await group_db.get_blacklist_stickers(chat_id)
    if not stickers:
        await message.reply_text(
            f"No blacklisted stickers in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
        )
        return

    text = f"<b>Blacklisted sticker sets in {html.escape(await get_chat_title(c, message.chat_id))}:</b>\n\n"
    for sticker in stickers:
        text += f"  \u2022 <code>{html.escape(sticker)}</code>\n"

    await message.reply_text(text)


@Client.on_updateNewMessage(filters=Filter.regex(r"(?i).+"))
async def blacklist_sticker_watcher(c: Client, update: types.UpdateNewMessage):
    message = update.message
    if not message:
        return

    chat_id = message.chat_id
    if chat_id > 0:
        return

    user_id = message.from_id
    if not user_id:
        return

    if await is_admin(c, chat_id, user_id):
        return

    content = message.content
    if not isinstance(content, types.MessageSticker):
        return

    sticker = content.sticker
    sticker_set = await c.getStickerSet(set_id=sticker.set_id)
    if isinstance(sticker_set, types.Error) or not sticker_set or not sticker_set.name:
        return

    set_name_lower = sticker_set.name.lower()
    blacklist_stickers = await group_db.get_blacklist_stickers(chat_id)
    if not blacklist_stickers:
        return

    for trigger in blacklist_stickers:
        if set_name_lower == trigger.lower():
            await delete_message(c, chat_id, message.id)
            break
