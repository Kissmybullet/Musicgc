#  Ported from LadyRezebb-reference/MukeshRobot/modules/userinfo.py
#  Group management: User info, ID, bio

import html

from pytdbot import Client, types

from src.core import (
    Filter,
    group_db,
    DRAGONS,
    DEMONS,
    TIGERS,
    WOLVES,
    OWNER_ID,
    DEV_USERS,
)
from src.core._admins import is_admin
from src.modules._helpers import (
    get_reply_user,
    get_user_id,
    get_user_name,
)

__mod_name__ = "Info"
__help__ = """
<b>ID:</b>
/id - Get the current group ID. If used by replying, gets that user's ID.
<b>Bio:</b>
/bio - Get your or another user's bio.
/setbio &lt;text&gt; - While replying, will save another user's bio.
<b>Overall info about a user:</b>
/info - Get information about a user.
"""


@Client.on_message(filters=Filter.command("id"))
async def id_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    args = message.text.split(None, 1)

    target_id = await get_reply_user(message)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if target_id:
        user = await c.getUser(user_id=target_id)
        if isinstance(user, types.Error):
            await message.reply_text(f"<code>{target_id}</code>")
            return

        name = user.first_name or str(target_id)
        await message.reply_text(
            f"<b>{html.escape(name)}</b>'s ID is <code>{target_id}</code>."
        )
    else:
        if chat_id > 0:
            await message.reply_text(f"Your ID is <code>{chat_id}</code>.")
        else:
            await message.reply_text(f"This group's ID is <code>{chat_id}</code>.")


@Client.on_message(filters=Filter.command("info"))
async def info_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    args = message.text.split(None, 1)

    target_id = await get_reply_user(message)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        target_id = message.from_id

    if not target_id:
        await message.reply_text(
            "Please reply to a user or provide a user ID/username."
        )
        return

    rep = await message.reply_text("<code>Extracting information...</code>")

    user = await c.getUser(user_id=target_id)
    if isinstance(user, types.Error):
        await rep.edit_text("Failed to get user info.")
        return

    name = user.first_name or str(target_id)
    text = f"<b>User Info</b>\n\n"
    text += f"<b>User ID:</b> <code>{user.id}</code>\n"
    text += f"<b>First Name:</b> {html.escape(name)}\n"

    if user.last_name:
        text += f"<b>Last Name:</b> {html.escape(user.last_name)}\n"

    if user.usernames and user.usernames.editable_username:
        text += f"<b>Username:</b> @{html.escape(user.usernames.editable_username)}\n"

    text += f"<b>Link:</b> <a href='tg://user?id={user.id}'>Profile</a>\n"

    if chat_id < 0 and target_id != c.me.id:
        member = await c.getChatMember(
            chat_id=chat_id,
            member_id=types.MessageSenderUser(user_id=target_id),
        )
        if member and not isinstance(member, types.Error):
            status = member.status
            if isinstance(status, types.ChatMemberStatusBanned):
                text += "\n<b>Presence:</b> <code>Banned/Left</code>\n"
            elif isinstance(status, types.ChatMemberStatusRestricted):
                text += "\n<b>Presence:</b> <code>Restricted</code>\n"
            elif isinstance(status, types.ChatMemberStatusAdministrator):
                text += "\n<b>Presence:</b> <code>Admin</code>\n"
                if hasattr(status, "custom_title") and status.custom_title:
                    text += f"<b>Custom Title:</b> {html.escape(status.custom_title)}\n"
            elif isinstance(status, types.ChatMemberStatusCreator):
                text += "\n<b>Presence:</b> <code>Owner</code>\n"
            else:
                text += "\n<b>Presence:</b> <code>Member</code>\n"

    disaster_level = ""
    if user.id == OWNER_ID:
        disaster_level = "God"
    elif user.id in DEV_USERS:
        disaster_level = "Hero Association"
    elif user.id in DRAGONS:
        disaster_level = "Dragon"
    elif user.id in DEMONS:
        disaster_level = "Demon"
    elif user.id in TIGERS:
        disaster_level = "Tiger"
    elif user.id in WOLVES:
        disaster_level = "Wolf"

    if disaster_level:
        text += f"\n<b>Disaster Level:</b> {disaster_level}\n"

    bio = await group_db.get_user_bio(target_id)
    if bio:
        text += f"\n<b>Bio:</b> {html.escape(bio)}\n"

    await rep.edit_text(text)


@Client.on_message(filters=Filter.command("bio"))
async def bio_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    args = message.text.split(None, 1)

    target_id = await get_reply_user(message)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        target_id = message.from_id

    bio = await group_db.get_user_bio(target_id)
    if bio:
        name = await get_user_name(c, target_id)
        await message.reply_text(f"<b>{html.escape(name)}</b>:\n{html.escape(bio)}")
    else:
        name = await get_user_name(c, target_id)
        await message.reply_text(
            f"{name} hasn't had a bio set about themselves yet!\nSet one using /setbio"
        )


@Client.on_message(filters=Filter.command("setbio"))
async def setbio_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not message.reply_to_message_id:
        await message.reply_text("Reply to someone to set their bio!")
        return

    replied = await message.getRepliedMessage()
    if isinstance(replied, types.Error):
        await message.reply_text("Failed to get the replied message.")
        return

    if not replied.sender_id or not isinstance(
        replied.sender_id, types.MessageSenderUser
    ):
        await message.reply_text("Cannot identify the replied user.")
        return

    target_id = replied.sender_id.user_id

    if target_id == user_id:
        await message.reply_text(
            "Ha, you can't set your own bio! You're at the mercy of others here."
        )
        return

    if target_id == c.me.id:
        await message.reply_text("I only trust my owner to set my bio.")
        return

    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text(
            "Please provide the bio text.\nExample: <code>/setbio This user is great</code>"
        )
        return

    bio_text = args[1].strip()
    if len(bio_text) > 1000:
        await message.reply_text("Bio needs to be under 1000 characters!")
        return

    await group_db.set_user_bio(target_id, bio_text)
    name = await get_user_name(c, target_id)
    await message.reply_text(f"Updated {name}'s bio!")
