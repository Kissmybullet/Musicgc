#  Ported from LadyRezebb-reference/MukeshRobot/modules/approve.py
#  Group management: Approve/Unapprove users

import html

from pytdbot import Client, types

from src.core import Filter, group_db, DRAGONS
from src.core._admins import is_admin, is_owner, load_admin_cache
from src.modules._helpers import (
    get_reply_user,
    get_user_id,
    get_user_mention,
    get_user_name,
    is_user_admin_in_chat,
)

__mod_name__ = "Approve"
__help__ = """
<b>Approve Commands:</b>
Sometimes you might trust a user not to send unwanted content. Maybe not enough
to make them an admin, but you might be OK with locks, blacklists, and antiflood
not applying to them.

<b>Admin commands:</b>
/approve - Approve of a user. Locks, blacklists, and antiflood won't apply to them anymore.
/unapprove - Unapprove of a user. They will now be subject to locks, blacklists, and antiflood again.
/approved - List all approved users.
/unapproveall - Unapprove ALL users in a chat. This cannot be undone.
"""


@Client.on_message(filters=Filter.command("approve"))
async def approve_cmd(c: Client, message: types.Message):
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

    target_id = await get_reply_user(message)
    args = message.text.split(None, 1)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return

    if await is_user_admin_in_chat(c, chat_id, target_id):
        await message.reply_text(
            "User is already admin - locks, blocklists, and antiflood already don't apply to them."
        )
        return

    if await group_db.is_approved(chat_id, target_id):
        name = await get_user_mention(c, target_id)
        await message.reply_text(f"{name} is already approved in this chat.")
        return

    await group_db.approve_user(chat_id, target_id)
    name = await get_user_mention(c, target_id)
    await message.reply_text(
        f"{name} has been approved in this chat! They will now be ignored by "
        "automated admin actions like locks, blocklists, and antiflood."
    )


@Client.on_message(filters=Filter.command(["unapprove", "disapprove"]))
async def disapprove_cmd(c: Client, message: types.Message):
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

    target_id = await get_reply_user(message)
    args = message.text.split(None, 1)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return

    if await is_user_admin_in_chat(c, chat_id, target_id):
        await message.reply_text("This user is an admin, they can't be unapproved.")
        return

    if not await group_db.is_approved(chat_id, target_id):
        name = await get_user_name(c, target_id)
        await message.reply_text(f"{name} isn't approved yet!")
        return

    await group_db.unapprove_user(chat_id, target_id)
    name = await get_user_name(c, target_id)
    chat_info = await c.getChat(chat_id=chat_id)
    chat_title = (
        chat_info.title if not isinstance(chat_info, types.Error) else "this chat"
    )
    await message.reply_text(f"{name} is no longer approved in {chat_title}.")


@Client.on_message(filters=Filter.command("approved"))
async def approved_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    approved_users = await group_db.get_approved_users(chat_id)
    if not approved_users:
        chat_info = await c.getChat(chat_id=chat_id)
        chat_title = (
            chat_info.title if not isinstance(chat_info, types.Error) else "this chat"
        )
        await message.reply_text(f"No users are approved in {chat_title}.")
        return

    msg = "<b>Approved users:</b>\n"
    for uid in approved_users:
        name = await get_user_name(c, uid)
        msg += f"- <code>{uid}</code>: {html.escape(name)}\n"
    await message.reply_text(msg)


@Client.on_message(filters=Filter.command("unapproveall"))
async def unapproveall_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    is_chat_owner = await is_owner(c, chat_id, user_id)
    if not is_chat_owner and user_id not in DRAGONS:
        await message.reply_text("Only the chat owner can unapprove all users at once.")
        return

    await group_db.unapprove_all(chat_id)
    await message.reply_text("All users have been unapproved.")
