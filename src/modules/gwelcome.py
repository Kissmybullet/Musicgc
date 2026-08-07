#  Ported from LadyRezebb-reference/MukeshRobot/modules/welcome.py
#  Group management: Welcome and Goodbye messages

import html
import random

from pytdbot import Client, types

from src.core import Filter, group_db
from src.core._admins import is_admin, load_admin_cache
from src.modules._helpers import (
    delete_message,
    get_chat_member_count,
    get_chat_title,
    get_user_mention,
    send_message,
)

__mod_name__ = "Welcome"
__help__ = """
<b>Welcome/Goodbye Commands:</b>
/welcome - Show current welcome settings
/welcome on/off - Enable or disable welcome messages
/goodbye on/off - Enable or disable goodbye messages
/setwelcome &lt;text&gt; - Set a custom welcome message
/setgoodbye &lt;text&gt; - Set a custom goodbye message
/resetwelcome - Reset welcome to default
/resetgoodbye - Reset goodbye to default

<b>Welcome Variables:</b>
{first} - User's first name
{last} - User's last name
{fullname} - User's full name
{username} - User's @username
{mention} - Mention the user
{id} - User's ID
{count} - Member count
{chatname} - Chat title
"""

DEFAULT_WELCOME = "Hey {first}, welcome to {chatname}!"
DEFAULT_GOODBYE = "Nice knowing you, {first}!"


@Client.on_message(filters=Filter.command("welcome"))
async def welcome_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id
    args = message.text.split()

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    if len(args) >= 2 and args[1].lower() in ("on", "yes"):
        await group_db.set_welcome(chat_id, {"welcome_enabled": True})
        await message.reply_text("Welcome messages enabled!")
        return

    if len(args) >= 2 and args[1].lower() in ("off", "no"):
        await group_db.set_welcome(chat_id, {"welcome_enabled": False})
        await message.reply_text("Welcome messages disabled!")
        return

    data = await group_db.get_welcome(chat_id) or {}
    enabled = data.get("welcome_enabled", True)
    welcome_text = data.get("welcome_text", DEFAULT_WELCOME)
    goodbye_text = data.get("goodbye_text", DEFAULT_GOODBYE)
    goodbye_enabled = data.get("goodbye_enabled", True)

    await message.reply_text(
        f"<b>Welcome settings for {html.escape(await get_chat_title(c, message.chat_id))}:</b>\n\n"
        f"<b>Welcome:</b> {'Enabled' if enabled else 'Disabled'}\n"
        f"<b>Goodbye:</b> {'Enabled' if goodbye_enabled else 'Disabled'}\n\n"
        f"<b>Welcome message:</b>\n{welcome_text}\n\n"
        f"<b>Goodbye message:</b>\n{goodbye_text}"
    )


@Client.on_message(filters=Filter.command("setwelcome"))
async def set_welcome_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split(None, 1)
    if len(args) < 2 or not args[1].strip():
        await message.reply_text(
            "Please provide the welcome message text.\n"
            "Available variables: {first}, {last}, {fullname}, {username}, "
            "{mention}, {id}, {count}, {chatname}"
        )
        return

    welcome_text = args[1].strip()
    await group_db.set_welcome(
        chat_id,
        {"welcome_text": welcome_text, "welcome_enabled": True},
    )
    await message.reply_text("Successfully set custom welcome message!")


@Client.on_message(filters=Filter.command("setgoodbye"))
async def set_goodbye_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split(None, 1)
    if len(args) < 2 or not args[1].strip():
        await message.reply_text(
            "Please provide the goodbye message text.\n"
            "Available variables: {first}, {last}, {fullname}, {username}, "
            "{mention}, {id}, {count}, {chatname}"
        )
        return

    goodbye_text = args[1].strip()
    await group_db.set_welcome(
        chat_id,
        {"goodbye_text": goodbye_text, "goodbye_enabled": True},
    )
    await message.reply_text("Successfully set custom goodbye message!")


@Client.on_message(filters=Filter.command("resetwelcome"))
async def reset_welcome_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    await group_db.set_welcome(
        chat_id,
        {"welcome_text": DEFAULT_WELCOME, "welcome_enabled": True},
    )
    await message.reply_text("Successfully reset welcome message to default!")


@Client.on_message(filters=Filter.command("resetgoodbye"))
async def reset_goodbye_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    await group_db.set_welcome(
        chat_id,
        {"goodbye_text": DEFAULT_GOODBYE, "goodbye_enabled": True},
    )
    await message.reply_text("Successfully reset goodbye message to default!")


def _format_welcome(text: str, user, chat_title: str, count: int) -> str:
    first = getattr(user, "first_name", None) or "User"
    last = getattr(user, "last_name", "") or ""
    fullname = f"{first} {last}".strip() if last else first
    username = (
        f"@{user.username}" if getattr(user, "username", None) else mention_str(user)
    )
    mention = mention_str(user)
    uid = getattr(user, "id", 0)

    return text.format(
        first=html.escape(first),
        last=html.escape(last),
        fullname=html.escape(fullname),
        username=html.escape(username) if username.startswith("@") else username,
        mention=mention,
        id=uid,
        count=count,
        chatname=html.escape(chat_title),
    )


def mention_str(user) -> str:
    uid = getattr(user, "id", 0)
    name = getattr(user, "first_name", None) or "User"
    return f'<a href="tg://user?id={uid}">{html.escape(name)}</a>'


async def _handle_new_member(c: Client, chat_id: int, new_member, chat_title: str):
    data = await group_db.get_welcome(chat_id) or {}
    if not data.get("welcome_enabled", True):
        return

    welcome_text = data.get("welcome_text", DEFAULT_WELCOME)

    try:
        count = await get_chat_member_count(c, chat_id)
    except Exception:
        count = 0

    text = _format_welcome(welcome_text, new_member, chat_title, count)

    await send_message(c, chat_id, text)


async def _handle_leave_member(c: Client, chat_id: int, left_member, chat_title: str):
    data = await group_db.get_welcome(chat_id) or {}
    if not data.get("goodbye_enabled", True):
        return

    goodbye_text = data.get("goodbye_text", DEFAULT_GOODBYE)

    try:
        count = await get_chat_member_count(c, chat_id)
    except Exception:
        count = 0

    text = _format_welcome(goodbye_text, left_member, chat_title, count)

    await send_message(c, chat_id, text)


@Client.on_updateNewMessage(filters=Filter.regex(r".*"))
async def welcome_watcher(c: Client, update: types.UpdateNewMessage):
    message = update.message
    if not message:
        return

    chat_id = message.chat_id
    if chat_id > 0:
        return

    content = message.content

    if isinstance(content, types.MessageChatAddMembers):
        for new_member in content.member_user_ids:
            user_result = await c.getUser(user_id=new_member)
            if isinstance(user_result, types.Error):
                continue
            chat_info = await c.getChat(chat_id=chat_id)
            chat_title = (
                chat_info.title
                if not isinstance(chat_info, types.Error)
                else "this chat"
            )
            await _handle_new_member(c, chat_id, user_result, chat_title)

    elif isinstance(content, types.MessageChatDeleteMember):
        left_user_id = content.user_id
        if left_user_id == c.me.id:
            return
        user_result = await c.getUser(user_id=left_user_id)
        if isinstance(user_result, types.Error):
            return
        chat_info = await c.getChat(chat_id=chat_id)
        chat_title = (
            chat_info.title if not isinstance(chat_info, types.Error) else "this chat"
        )
        await _handle_leave_member(c, chat_id, user_result, chat_title)
