#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core import db
from src.core import admins_only

__mod_name__ = "Global Bans"
__help__ = """
*✿ Gʟᴏʙᴀʟ ʙᴀɴ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /gban <user> <reason> ➛ Globally bans a user across all chats where the bot is admin.
❍ /ungban <user> ➛ Removes a global ban.
❍ /gbanlist ➛ Shows all globally banned users.
"""


@Client.on_message(filters=Filter.command(["gban"]))
@admins_only(only_owner=True)
async def gban_cmd(c: Client, message: Message):
    """Globally bans a user."""
    chat_id = message.chat_id
    args = message.text.split(maxsplit=2)

    target_user_id = None
    if message.reply_to_message_id:
        replied = await c.getMessage(chat_id, message.reply_to_message_id)
        if replied and hasattr(replied, "from_id"):
            target_user_id = replied.from_id
    elif len(args) > 1:
        try:
            target_user_id = int(args[1])
        except ValueError:
            pass

    if not target_user_id:
        return await message.reply_text("Please reply to a user or provide their ID.")

    reason = args[2] if len(args) > 2 else "No reason provided"

    is_gbanned = await db.group.is_gbanned(target_user_id)
    if is_gbanned:
        return await message.reply_text("User is already globally banned.")

    # Attempt to fetch user's name
    name = "Unknown"
    user_info = await c.getUser(user_id=target_user_id)
    if not isinstance(user_info, types.Error):
        name = user_info.first_name

    await db.group.gban(target_user_id, name, reason)
    await message.reply_text(
        f"Globally banned `{target_user_id}` for: {reason}", parse_mode="markdown"
    )


@Client.on_message(filters=Filter.command(["ungban"]))
@admins_only(only_owner=True)
async def ungban_cmd(c: Client, message: Message):
    """Removes a global ban."""
    chat_id = message.chat_id
    args = message.text.split(maxsplit=1)

    target_user_id = None
    if message.reply_to_message_id:
        replied = await c.getMessage(chat_id, message.reply_to_message_id)
        if replied and hasattr(replied, "from_id"):
            target_user_id = replied.from_id
    elif len(args) > 1:
        try:
            target_user_id = int(args[1])
        except ValueError:
            pass

    if not target_user_id:
        return await message.reply_text("Please reply to a user or provide their ID.")

    is_gbanned = await db.group.is_gbanned(target_user_id)
    if not is_gbanned:
        return await message.reply_text("User is not globally banned.")

    await db.group.ungban(target_user_id)
    await message.reply_text(
        f"Removed global ban for `{target_user_id}`.", parse_mode="markdown"
    )


@Client.on_message(filters=Filter.command(["gbanlist"]))
@admins_only(only_owner=True)
async def gbanlist_cmd(c: Client, message: Message):
    """Lists all globally banned users."""
    bans = await db.group.get_gban_list()
    if not bans:
        return await message.reply_text("No globally banned users.")

    text = "**Globally Banned Users:**\n\n"
    for idx, ban in enumerate(bans, 1):
        text += f"{idx}. `{ban['_id']}` - {ban.get('name', 'Unknown')} (Reason: {ban.get('reason', 'None')})\n"

    await message.reply_text(text, parse_mode="markdown")


# Listener to enforce global bans
@Client.on_message()
async def enforce_gbans(c: Client, message: Message):
    """Checks if a sender is gbanned and removes them if they are."""
    if getattr(message, "chat_id", 0) >= 0:
        return

    user_id = message.from_id
    if not user_id:
        return

    # Check if chat enforces gbans
    gban_enabled = await db.group.get_gban_setting(message.chat_id)
    if not gban_enabled:
        return

    if await db.group.is_gbanned(user_id):
        try:
            await c.banChatMember(message.chat_id, user_id)
            await message.reply_text(
                f"Globally banned user `{user_id}` was automatically removed.",
                parse_mode="markdown",
            )
        except Exception:
            pass
