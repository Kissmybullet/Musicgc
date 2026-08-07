#  Ported from LadyRezebb-reference/MukeshRobot/modules/admin.py
#  Group management: Promote, Demote, SetSticker, SetChatPic, SetChatDesc, SetChatTitle, AdminList

import html
import os
import tempfile

from pytdbot import Client, types

from src.core import Filter, config
from src.core._admins import is_admin, load_admin_cache
from src.modules._helpers import (
    ban_user,
    delete_message,
    get_admins,
    get_chat_info,
    get_chat_member,
    get_chat_title,
    get_reply_user,
    get_user_id,
    get_user_mention,
    get_user_name,
    is_user_admin_in_chat,
    send_message,
    unban_user,
)

__mod_name__ = "Admin"
__help__ = """
<b>Admin Commands:</b>
/promote - Promote a user (reply or provide ID/username)
/demote - Demote an admin (reply or provide ID/username)
/setsticker - Reply to a sticker to set it as group sticker pack
/setchatpic - Reply to a photo to set as group profile pic
/setchatdesc &lt;text&gt; - Set group description
/setchattitle &lt;text&gt; - Set group title
/adminlist - List all admins in the chat
"""


@Client.on_message(filters=Filter.command("promote"))
async def promote_cmd(c: Client, message: types.Message):
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
    args = message.text.split(None, 2)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text("Reply to a user or provide a user ID/username.")
        return

    if target_id == c.me.id:
        await message.reply_text("I can't promote myself.")
        return

    if await is_user_admin_in_chat(c, chat_id, target_id):
        await message.reply_text("That user is already an admin.")
        return

    rights = types.ChatAdministratorRights(
        can_manage_chat=True,
        can_change_info=True,
        can_delete_messages=True,
        can_invite_users=True,
        can_restrict_members=True,
        can_pin_messages=True,
        can_promote_members=False,
        can_manage_video_chats=True,
    )

    status = types.ChatMemberStatusAdministrator(rights=rights)
    result = await c.setChatMemberStatus(
        chat_id=chat_id,
        member_id=types.MessageSenderUser(user_id=target_id),
        status=status,
    )

    if isinstance(result, types.Error):
        await message.reply_text(f"Failed to promote: {result.message}")
        return

    name = await get_user_mention(c, target_id)
    promoter = await get_user_mention(c, user_id)
    await message.reply_text(f"<b>Promoted</b> {name}\n<b>Promoted by:</b> {promoter}")


@Client.on_message(filters=Filter.command("demote"))
async def demote_cmd(c: Client, message: types.Message):
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
    args = message.text.split(None, 2)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])

    if not target_id:
        await message.reply_text("Reply to a user or provide a user ID/username.")
        return

    if target_id == c.me.id:
        await message.reply_text("I can't demote myself.")
        return

    member = await get_chat_member(c, chat_id, target_id)
    if not member:
        await message.reply_text("User not found in this chat.")
        return

    if isinstance(member.status, types.ChatMemberStatusCreator):
        await message.reply_text("I can't demote the chat owner.")
        return

    if not isinstance(member.status, types.ChatMemberStatusAdministrator):
        await message.reply_text("That user is not an admin.")
        return

    no_rights = types.ChatAdministratorRights(
        can_manage_chat=False,
        can_change_info=False,
        can_delete_messages=False,
        can_invite_users=False,
        can_restrict_members=False,
        can_pin_messages=False,
        can_promote_members=False,
        can_manage_video_chats=False,
    )

    status = types.ChatMemberStatusAdministrator(rights=no_rights)
    result = await c.setChatMemberStatus(
        chat_id=chat_id,
        member_id=types.MessageSenderUser(user_id=target_id),
        status=status,
    )

    if isinstance(result, types.Error):
        await message.reply_text(f"Failed to demote: {result.message}")
        return

    name = await get_user_mention(c, target_id)
    demoter = await get_user_mention(c, user_id)
    await message.reply_text(f"<b>Demoted</b> {name}\n<b>Demoted by:</b> {demoter}")


@Client.on_message(filters=Filter.command("setsticker"))
async def set_sticker_cmd(c: Client, message: types.Message):
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

    if not message.reply_to_message_id:
        await message.reply_text("Reply to a sticker to set it as group sticker pack.")
        return

    replied = await message.getRepliedMessage()
    if isinstance(replied, types.Error) or not replied:
        await message.reply_text("Could not fetch the replied message.")
        return

    if not isinstance(replied.content, types.MessageSticker):
        await message.reply_text("Reply to a sticker to set it as group sticker pack.")
        return

    sticker_set_id = replied.content.sticker.set_id
    if not sticker_set_id:
        await message.reply_text("Could not get the sticker set ID.")
        return

    chat = await c.getChat(chat_id=chat_id)
    if isinstance(chat, types.Error) or not isinstance(chat.type, types.ChatTypeSupergroup):
        await message.reply_text("This command only works in supergroups.")
        return

    result = await c.setSupergroupStickerSet(
        supergroup_id=chat.type.supergroup_id, sticker_set_id=sticker_set_id
    )

    if isinstance(result, types.Error):
        if "Participants too few" in result.message:
            await message.reply_text(
                "Your group needs minimum 100 members for setting a sticker pack."
            )
        else:
            await message.reply_text(f"Error: {result.message}")
        return

    await message.reply_text(
        f"Successfully set group sticker pack in {await get_chat_title(c, message.chat_id)}!"
    )


@Client.on_message(filters=Filter.command(["setchatpic", "setgpic"]))
async def set_chat_pic_cmd(c: Client, message: types.Message):
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

    if not message.reply_to_message_id:
        await message.reply_text(
            "Reply to a photo or document to set as group profile pic."
        )
        return

    replied = await message.getRepliedMessage()
    if isinstance(replied, types.Error) or not replied:
        await message.reply_text("Could not fetch the replied message.")
        return

    if isinstance(replied.content, types.MessagePhoto):
        file_id = (
            replied.content.photo.sizes[-1].photo.id
            if replied.content.photo.sizes
            else None
        )
    elif isinstance(replied.content, types.MessageDocument):
        file_id = replied.content.document.document.id
    else:
        await message.reply_text(
            "Reply to a photo or document to set as group profile pic."
        )
        return

    if not file_id:
        await message.reply_text("Could not get the file from the replied message.")
        return

    result = await c.setChatPhoto(
        chat_id=chat_id,
        photo=types.InputChatPhotoStatic(photo=types.InputFileId(id=file_id)),
    )

    if isinstance(result, types.Error):
        await message.reply_text(f"Error: {result.message}")
        return

    await message.reply_text("Successfully set group profile pic!")

@Client.on_message(filters=Filter.command(["rmchatpic", "rmgpic"]))
async def rm_chat_pic_cmd(c: Client, message: types.Message):
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

    result = await c.setChatPhoto(
        chat_id=chat_id,
        photo=None,
    )

    if isinstance(result, types.Error):
        await message.reply_text(f"Error: {result.message}")
        return

    await message.reply_text("Successfully removed group profile pic!")


@Client.on_message(filters=Filter.command("setchatdesc"))
async def set_chat_desc_cmd(c: Client, message: types.Message):
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

    args = message.text.split(None, 1)
    if len(args) < 2 or not args[1].strip():
        await message.reply_text("Enter some text to set as group description.")
        return

    desc = args[1].strip()
    if len(desc) > 255:
        await message.reply_text("Description must be less than 255 characters.")
        return

    result = await c.setChatDescription(chat_id=chat_id, description=desc)

    if isinstance(result, types.Error):
        await message.reply_text(f"Error: {result.message}")
        return

    await message.reply_text(
        f"Successfully updated chat description in {await get_chat_title(c, message.chat_id)}!"
    )


@Client.on_message(filters=Filter.command("setchattitle"))
async def set_chat_title_cmd(c: Client, message: types.Message):
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

    args = message.text.split(None, 1)
    if len(args) < 2 or not args[1].strip():
        await message.reply_text("Enter some text to set as new chat title.")
        return

    title = args[1].strip()

    result = await c.setChatTitle(chat_id=chat_id, title=title)

    if isinstance(result, types.Error):
        await message.reply_text(f"Error: {result.message}")
        return

    await message.reply_text(
        f"Successfully set <b>{html.escape(title)}</b> as new chat title!"
    )


@Client.on_message(filters=Filter.command("adminlist"))
async def adminlist_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    msg = await message.reply_text("Fetching admins list...")

    members = await get_admins(c, chat_id)
    if not members:
        await msg.edit_text("Failed to fetch admin list.")
        return

    text = (
        f"Admins in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>:\n\n"
    )

    owner_list = []
    admin_list = []
    custom_title_map = {}

    for member in members:
        member_id = member.member_id
        if not isinstance(member_id, types.MessageSenderUser):
            continue

        uid = member_id.user_id
        status = member.status

        name = await get_user_mention(c, uid)

        if isinstance(status, types.ChatMemberStatusCreator):
            owner_list.append(name)
            if status.custom_title:
                owner_list.append(
                    f"  <code>┗━ {html.escape(status.custom_title)}</code>"
                )
        elif isinstance(status, types.ChatMemberStatusAdministrator):
            custom_title = getattr(status, "custom_title", "")
            if custom_title:
                if custom_title not in custom_title_map:
                    custom_title_map[custom_title] = []
                custom_title_map[custom_title].append(name)
            else:
                admin_list.append(name)

    if owner_list:
        text += "🥀 <b>Owner:</b>\n"
        for item in owner_list:
            text += f"  • {item}\n"

    if admin_list:
        text += "\n💫 <b>Admins:</b>\n"
        for admin in admin_list:
            text += f"  • {admin}\n"

    if custom_title_map:
        text += "\n🔮 <b>Custom Titles:</b>\n"
        for title, admins in custom_title_map.items():
            text += f"  <code>{html.escape(title)}</code>\n"
            for admin in admins:
                text += f"    • {admin}\n"

    await msg.edit_text(text)
