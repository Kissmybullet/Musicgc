#  Ported from LadyRezebb-reference/MukeshRobot/modules/locks.py
#  Group management: Lock/Unlock chat content types, message watcher

import html
import re

from pytdbot import Client, types

from src.core import Filter, group_db
from src.core._admins import is_admin, is_owner, load_admin_cache
from src.modules._helpers import (
    delete_message,
    get_chat_title,
    get_user_mention,
    is_user_admin_in_chat,
    send_message,
)

__mod_name__ = "Locks"
__help__ = """
<b>Lock Commands:</b>
/locktypes - List all available lock types
/lock &lt;type&gt; - Lock a content type for non-admins
/unlock &lt;type&gt; - Unlock a content type for everyone
/locked - Show all current lock states

<b>Lock Types:</b>
text, media, sticker, gif, poll, url, inline, button,
game, location, forward, contact, audio, video, photo,
voice, document, all
"""

VALID_LOCK_TYPES = {
    "text",
    "media",
    "sticker",
    "gif",
    "poll",
    "url",
    "inline",
    "button",
    "game",
    "location",
    "forward",
    "contact",
    "audio",
    "video",
    "photo",
    "voice",
    "document",
    "all",
}


def _get_message_text(message: types.Message) -> str:
    content = message.content
    if isinstance(content, types.MessageText):
        return content.text.text or ""
    return ""


def _has_forward(message: types.Message) -> bool:
    return message.forward_origin is not None


def _has_url(message: types.Message) -> bool:
    content = message.content
    if isinstance(content, types.MessageText):
        text = content.text.text or ""
        return bool(re.search(r"https?://[^\s]+", text))
    if isinstance(content, types.MessagePhoto):
        caption = content.caption or ""
        return bool(re.search(r"https?://[^\s]+", caption))
    if isinstance(content, types.MessageVideo):
        caption = content.caption or ""
        return bool(re.search(r"https?://[^\s]+", caption))
    if isinstance(content, types.MessageDocument):
        caption = content.caption or ""
        return bool(re.search(r"https?://[^\s]+", caption))
    return False


def _has_button(message: types.Message) -> bool:
    content = message.content
    if isinstance(content, types.MessageText):
        reply_markup = (
            content.text._reply_markup
            if hasattr(content.text, "_reply_markup")
            else None
        )
        if reply_markup and hasattr(reply_markup, "rows"):
            return bool(reply_markup.rows)
    return False


def _has_inline(message: types.Message) -> bool:
    content = message.content
    if isinstance(content, types.MessageText):
        text = content.text.text or ""
        if text.startswith("@") and len(text.split()) == 1:
            return True
    return False


def _is_media(message: types.Message) -> bool:
    content = message.content
    media_types = (
        types.MessagePhoto,
        types.MessageVideo,
        types.MessageAnimation,
        types.MessageDocument,
        types.MessageAudio,
        types.MessageVoice,
        types.MessageVideoNote,
        types.MessageSticker,
    )
    return isinstance(content, media_types)


def _matches_lock(message: types.Message, lock_type: str) -> bool:
    content = message.content

    if lock_type == "text":
        return isinstance(content, types.MessageText)
    elif lock_type == "sticker":
        return isinstance(content, types.MessageSticker)
    elif lock_type == "gif":
        return isinstance(content, types.MessageAnimation)
    elif lock_type == "poll":
        return isinstance(content, types.MessagePoll)
    elif lock_type == "url":
        return _has_url(message)
    elif lock_type == "inline":
        return _has_inline(message)
    elif lock_type == "button":
        return _has_button(message)
    elif lock_type == "game":
        return isinstance(content, types.MessageGame)
    elif lock_type == "location":
        return isinstance(content, types.MessageLocation)
    elif lock_type == "forward":
        return _has_forward(message)
    elif lock_type == "contact":
        return isinstance(content, types.MessageContact)
    elif lock_type == "audio":
        return isinstance(content, types.MessageAudio)
    elif lock_type == "video":
        return isinstance(content, types.MessageVideo)
    elif lock_type == "photo":
        return isinstance(content, types.MessagePhoto)
    elif lock_type == "voice":
        return isinstance(content, types.MessageVoice)
    elif lock_type == "document":
        return isinstance(content, types.MessageDocument)
    elif lock_type == "media":
        return _is_media(message)
    elif lock_type == "all":
        return True
    return False


@Client.on_message(filters=Filter.command("locktypes"))
async def locktypes_cmd(c: Client, message: types.Message):
    types_list = "\n  • ".join(sorted(VALID_LOCK_TYPES))
    await message.reply_text(f"<b>Available lock types:</b>\n\n  • {types_list}")


@Client.on_message(filters=Filter.command("lock"))
async def lock_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("What are you trying to lock?")
        return

    lock_type = args[1].lower()
    if lock_type not in VALID_LOCK_TYPES:
        await message.reply_text(
            "Invalid lock type! Use /locktypes to see available types."
        )
        return

    await group_db.set_lock(chat_id, lock_type, True)
    await message.reply_text(f"Locked <b>{html.escape(lock_type)}</b> for non-admins!")


@Client.on_message(filters=Filter.command("unlock"))
async def unlock_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("What are you trying to unlock?")
        return

    lock_type = args[1].lower()
    if lock_type not in VALID_LOCK_TYPES:
        await message.reply_text(
            "Invalid lock type! Use /locktypes to see available types."
        )
        return

    await group_db.set_lock(chat_id, lock_type, False)
    await message.reply_text(f"Unlocked <b>{html.escape(lock_type)}</b> for everyone!")


@Client.on_message(filters=Filter.command("locked"))
async def locked_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    locks = await group_db.get_locks(chat_id)

    if not locks:
        await message.reply_text(
            f"No locks are set in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>."
        )
        return

    text = f"<b>Current locks in {html.escape(await get_chat_title(c, message.chat_id))}:</b>\n\n"

    all_types = sorted(VALID_LOCK_TYPES)
    for lock_type in all_types:
        is_locked = locks.get(lock_type, False)
        status = "Locked" if is_locked else "Unlocked"
        text += f"  • <b>{html.escape(lock_type)}</b>: {status}\n"

    await message.reply_text(text)


@Client.on_updateNewMessage(filters=Filter.regex(r"(?i).+"))
async def locks_watcher(c: Client, update: types.UpdateNewMessage):
    message = update.message
    if not message:
        return

    chat_id = message.chat_id
    if chat_id > 0:
        return

    user_id = message.from_id
    if not user_id:
        return

    if await is_user_admin_in_chat(c, chat_id, user_id):
        return

    locks = await group_db.get_locks(chat_id)
    if not locks:
        return

    for lock_type, is_locked in locks.items():
        if is_locked and _matches_lock(message, lock_type):
            await delete_message(c, chat_id, message.id)
            break
