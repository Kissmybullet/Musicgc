#  Ported from LadyRezebb-reference/MukeshRobot/modules/group.py
#  Group management: Group info, invite link

from pytdbot import Client, types

from src.core import Filter
from src.core._admins import is_admin, load_admin_cache
from src.modules._helpers import get_chat_member_count

__mod_name__ = "Group"
__help__ = """
<b>Group Commands:</b>
/groupinfo - Get information about this group
/invite - Generate an invite link for this group
"""


@Client.on_message(filters=Filter.command("groupinfo"))
async def groupinfo_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    chat = await c.getChat(chat_id=chat_id)
    if isinstance(chat, types.Error):
        await message.reply_text("Failed to get group info.")
        return

    text = f"<b>Group Info</b>\n\n"
    text += f"<b>Title:</b> {chat.title}\n"
    text += f"<b>ID:</b> <code>{chat.id}</code>\n"

    if hasattr(chat, "username") and chat.username:
        text += f"<b>Username:</b> @{chat.username}\n"

    if hasattr(chat, "description") and chat.description:
        text += f"<b>Description:</b> {chat.description.text}\n"

    member_count = await get_chat_member_count(c, chat_id)
    text += f"<b>Members:</b> {member_count}\n"

    if hasattr(chat, "permissions") and chat.permissions:
        perms = chat.permissions
        if hasattr(perms, "can_send_messages"):
            text += f"<b>Can send messages:</b> {perms.can_send_messages}\n"
        if hasattr(perms, "can_invite_users"):
            text += f"<b>Can invite users:</b> {perms.can_invite_users}\n"

    await message.reply_text(text)


@Client.on_message(filters=Filter.command("invite"))
async def invite_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    result = await c.createChatInviteLink(chat_id=chat_id)
    if isinstance(result, types.Error):
        await message.reply_text(
            "Failed to generate invite link. Check my permissions."
        )
        return

    invite_link = getattr(result, "invite_link", result.get("invite_link", "Unknown link")) if hasattr(result, "get") else getattr(result, "invite_link", "Unknown link")
    await message.reply_text(f"<b>Invite link:</b>\n{invite_link}")


@Client.on_message(filters=Filter.command("setgtitle"))
async def setgtitle_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text("Please provide a new title.")
        return

    new_title = args[1].strip()
    result = await c.setChatTitle(chat_id=chat_id, title=new_title)
    if isinstance(result, types.Error):
        await message.reply_text("Failed to set group title.")
        return

    await message.reply_text(f"Group title has been set to: <b>{new_title}</b>")


@Client.on_message(filters=Filter.command("setdescription"))
async def setdescription_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text("Please provide a new description.")
        return

    new_desc = args[1].strip()
    result = await c.setChatDescription(chat_id=chat_id, description=new_desc)
    if isinstance(result, types.Error):
        await message.reply_text("Failed to set group description.")
        return

    await message.reply_text("Group description has been updated.")
