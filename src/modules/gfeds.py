#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import uuid
from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core import db
from src.core import admins_only

__mod_name__ = "Feds"
__help__ = """
*✿ Fᴇᴅꜱ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /newfed <fedname> ➛ Create a new federation.
❍ /joinfed <fedid> ➛ Join a federation.
❍ /leavefed ➛ Leave the current federation.
❍ /fban <user> ➛ Ban a user across all chats in the fed.
❍ /unfban <user> ➛ Unban a user across the fed.
❍ /fedinfo <fedid> ➛ Get info about a federation.
"""


async def get_chat_fed(chat_id: int):
    """Finds the federation a chat is currently in."""
    # Find a fed where the chats array contains this chat_id
    doc = await db.group.feds_db.find_one({"chats": chat_id})
    return doc


@Client.on_message(filters=Filter.command(["newfed"]))
async def new_fed(c: Client, message: Message):
    """Creates a new federation."""
    user_id = message.from_id
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        return await message.reply_text("Please provide a name for your federation.")

    fed_name = args[1]
    fed_id = str(uuid.uuid4())[:8]  # Short unique ID

    await db.group.create_fed(fed_id, fed_name, user_id)
    await message.reply_text(
        f"Successfully created federation **{fed_name}**!\n\n**Fed ID:** `{fed_id}`\n\nUse this ID to link groups to your federation using `/joinfed {fed_id}`.",
        parse_mode="markdown",
    )


@Client.on_message(filters=Filter.command(["joinfed"]))
@admins_only()
async def join_fed(c: Client, message: Message):
    """Joins a federation."""
    chat_id = message.chat_id
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        return await message.reply_text(
            "Please provide the Federation ID you want to join."
        )

    fed_id = args[1]
    fed = await db.group.get_fed(fed_id)

    if not fed:
        return await message.reply_text("Invalid Federation ID.")

    current_fed = await get_chat_fed(chat_id)
    if current_fed:
        return await message.reply_text(
            f"This chat is already in the federation **{current_fed['name']}**. Please leave it first."
        )

    await db.group.join_fed(chat_id, fed_id)
    await message.reply_text(f"Successfully joined federation **{fed['name']}**!")


@Client.on_message(filters=Filter.command(["leavefed"]))
@admins_only()
async def leave_fed(c: Client, message: Message):
    """Leaves the current federation."""
    chat_id = message.chat_id

    current_fed = await get_chat_fed(chat_id)
    if not current_fed:
        return await message.reply_text("This chat is not currently in any federation.")

    await db.group.leave_fed(chat_id, current_fed["_id"])
    await message.reply_text(f"Successfully left federation **{current_fed['name']}**.")


@Client.on_message(filters=Filter.command(["fedinfo"]))
async def fed_info(c: Client, message: Message):
    """Gets info about a federation."""
    chat_id = message.chat_id
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        # Check current chat's fed
        current_fed = await get_chat_fed(chat_id)
        if not current_fed:
            return await message.reply_text(
                "Please provide a Federation ID or run this in a federated chat."
            )
        fed = current_fed
    else:
        fed_id = args[1]
        fed = await db.group.get_fed(fed_id)
        if not fed:
            return await message.reply_text("Invalid Federation ID.")

    name = fed["name"]
    fed_id = fed["_id"]
    creator = fed["creator"]
    num_chats = len(fed.get("chats", []))
    num_bans = len(fed.get("bans", []))

    text = (
        f"**Federation Info:**\n"
        f"**Name:** {name}\n"
        f"**ID:** `{fed_id}`\n"
        f"**Creator ID:** `{creator}`\n"
        f"**Linked Chats:** {num_chats}\n"
        f"**Banned Users:** {num_bans}"
    )
    await message.reply_text(text, parse_mode="markdown")


@Client.on_message(filters=Filter.command(["fban"]))
async def fed_ban(c: Client, message: Message):
    """Bans a user across the federation."""
    chat_id = message.chat_id
    user_id = message.from_id

    current_fed = await get_chat_fed(chat_id)
    if not current_fed:
        return await message.reply_text("This chat is not linked to any federation.")

    # Only creator can ban for now (a full implementation would have fed admins)
    if current_fed["creator"] != user_id:
        return await message.reply_text(
            "Only the Federation Creator can use this command."
        )

    args = message.text.split(maxsplit=2)
    reason = args[2] if len(args) > 2 else "No reason provided"

    target_user_id = None
    if message.reply_to_message_id:
        replied = await c.getMessage(chat_id, message.reply_to_message_id)
        if replied and getattr(replied, "from_id", None):
            target_user_id = replied.from_id
    elif len(args) > 1:
        try:
            target_user_id = int(args[1])
        except ValueError:
            pass

    if not target_user_id:
        return await message.reply_text("Please reply to a user or provide their ID.")

    await db.group.fed_ban(current_fed["_id"], target_user_id, reason)

    # We would theoretically broadcast the ban to all chats in current_fed["chats"] here,
    # but for now we just record it in the DB so future checks can apply it.
    await message.reply_text(
        f"New Federation Ban!\n**User:** `{target_user_id}`\n**Fed:** {current_fed['name']}\n**Reason:** {reason}",
        parse_mode="markdown",
    )


@Client.on_message(filters=Filter.command(["unfban"]))
async def fed_unban(c: Client, message: Message):
    """Unbans a user across the federation."""
    chat_id = message.chat_id
    user_id = message.from_id

    current_fed = await get_chat_fed(chat_id)
    if not current_fed:
        return await message.reply_text("This chat is not linked to any federation.")

    if current_fed["creator"] != user_id:
        return await message.reply_text(
            "Only the Federation Creator can use this command."
        )

    args = message.text.split(maxsplit=1)

    target_user_id = None
    if message.reply_to_message_id:
        replied = await c.getMessage(chat_id, message.reply_to_message_id)
        if replied and getattr(replied, "from_id", None):
            target_user_id = replied.from_id
    elif len(args) > 1:
        try:
            target_user_id = int(args[1])
        except ValueError:
            pass

    if not target_user_id:
        return await message.reply_text("Please reply to a user or provide their ID.")

    await db.group.fed_unban(current_fed["_id"], target_user_id)
    await message.reply_text(
        f"Unbanned user `{target_user_id}` from federation **{current_fed['name']}**.",
        parse_mode="markdown",
    )


# Listener to enforce fbans upon new users joining (basic implementation)
@Client.on_message()
async def enforce_fbans(c: Client, message: Message):
    """Checks if a sender is fbanned and removes them if they are."""
    if getattr(message, "chat_id", 0) >= 0:
        return
    chat_id = message.chat_id
    user_id = message.from_id

    # Only enforce if there is a sender and it's a regular message/join
    if not user_id:
        return

    current_fed = await get_chat_fed(chat_id)
    if not current_fed:
        return

    bans = current_fed.get("bans", [])
    banned_ids = [b["user_id"] for b in bans]

    if user_id in banned_ids:
        # User is federated banned!
        # Try to ban them from the group.
        try:
            await c.banChatMember(chat_id, user_id)
            await message.reply_text(
                f"Removed federated banned user `{user_id}` from this chat.\nFed: **{current_fed['name']}**",
                parse_mode="markdown",
            )
        except Exception:
            pass
