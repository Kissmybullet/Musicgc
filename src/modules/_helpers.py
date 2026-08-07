#  Common utilities for group-management modules ported from LadyRezebb.
#  Provides helper functions that bridge LadyRezebb's patterns with pytdbot's API.

import html
import time
from typing import Optional, Union

from pytdbot import Client, types

from src.core import (
    DRAGONS,
    DEV_USERS,
    DEMONS,
    TIGERS,
    WOLVES,
    OWNER_ID,
    SUPPORT_CHAT,
)


BOT_ID: int = 0


async def get_bot_id(c: Client) -> int:
    global BOT_ID
    if not BOT_ID:
        BOT_ID = c.me.id
    return BOT_ID


def is_user_admin(user_id: int) -> bool:
    return user_id in DRAGONS or user_id in DEV_USERS


def is_support(user_id: int) -> bool:
    return user_id in DEMONS


def is_tiger(user_id: int) -> bool:
    return user_id in TIGERS


def is_wolf(user_id: int) -> bool:
    return user_id in WOLVES


def is_bot_admin(user_id: int) -> bool:
    return user_id in DEV_USERS


def extract_user(message: types.Message) -> Optional[int]:
    if message.reply_to_message_id:
        return None
    args = message.text.split(None, 2)
    if len(args) >= 2:
        try:
            return int(args[1])
        except ValueError:
            pass
        target = args[1].lstrip("@")
        return target
    return None


async def get_user_id(c: Client, identifier: Union[int, str]) -> Optional[int]:
    if isinstance(identifier, int):
        return identifier
    if isinstance(identifier, str) and identifier.startswith("@"):
        username = identifier[1:]
        result = await c.searchPublicChat(username=username)
        if isinstance(result, types.Error):
            return None
        return result.id
    try:
        return int(identifier)
    except (ValueError, TypeError):
        return None


async def send_message(
    c: Client,
    chat_id: int,
    text: str,
    reply_to: Optional[int] = None,
    parse_mode: str = "html",
    disable_preview: bool = False,
) -> Union[types.Message, types.Error]:
    result = await c.sendTextMessage(
        chat_id=chat_id,
        text=text,
        parse_mode=parse_mode,
        disable_web_page_preview=disable_preview,
        reply_to_message_id=reply_to or 0,
    )
    return result


async def edit_message(
    c: Client,
    chat_id: int,
    message_id: int,
    text: str,
    disable_preview: bool = False,
) -> Union[types.Message, types.Error]:
    result = await c.editTextMessage(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        parse_mode="html",
        disable_web_page_preview=disable_preview,
    )
    return result


async def delete_message(c: Client, chat_id: int, message_id: int) -> bool:
    result = await c.deleteMessages(chat_id=chat_id, message_ids=[message_id])
    return not isinstance(result, types.Error)


async def ban_user(c: Client, chat_id: int, user_id: int) -> bool:
    result = await c.banChatMember(
        chat_id=chat_id, member_id=types.MessageSenderUser(user_id=user_id)
    )
    return not isinstance(result, types.Error)


async def unban_user(c: Client, chat_id: int, user_id: int) -> bool:
    result = await c.setChatMemberStatus(
        chat_id=chat_id,
        member_id=types.MessageSenderUser(user_id=user_id),
        status=types.ChatMemberStatusMember(),
    )
    return not isinstance(result, types.Error)


async def kick_user(c: Client, chat_id: int, user_id: int) -> bool:
    await ban_user(c, chat_id, user_id)
    return await unban_user(c, chat_id, user_id)


async def mute_user(
    c: Client, chat_id: int, user_id: int, until_date: Optional[int] = None
) -> bool:
    permissions = types.ChatPermissions(
        can_send_basic_messages=False,
        can_send_audios=False,
        can_send_photos=False,
        can_send_videos=False,
        can_send_video_notes=False,
        can_send_voice_notes=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_link_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False,
        can_create_topics=False,
    )
    result = await c.setChatMemberStatus(
        chat_id=chat_id,
        member_id=types.MessageSenderUser(user_id=user_id),
        status=types.ChatMemberStatusRestricted(
            is_member=True,
            restricted_until_date=until_date or 0,
            permissions=permissions,
        ),
    )
    return not isinstance(result, types.Error)


async def unmute_user(c: Client, chat_id: int, user_id: int) -> bool:
    permissions = types.ChatPermissions(
        can_send_basic_messages=True,
        can_send_audios=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_video_notes=True,
        can_send_voice_notes=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_link_previews=True,
        can_change_info=True,
        can_invite_users=True,
        can_pin_messages=True,
        can_create_topics=True,
    )
    result = await c.setChatMemberStatus(
        chat_id=chat_id,
        member_id=types.MessageSenderUser(user_id=user_id),
        status=types.ChatMemberStatusMember(),
    )
    return not isinstance(result, types.Error)


async def get_chat_info(c: Client, chat_id: int) -> Optional[types.Chat]:
    result = await c.getChat(chat_id=chat_id)
    if isinstance(result, types.Error):
        return None
    return result


async def get_chat_member(
    c: Client, chat_id: int, user_id: int
) -> Optional[types.ChatMember]:
    result = await c.getChatMember(
        chat_id=chat_id, member_id=types.MessageSenderUser(user_id=user_id)
    )
    if isinstance(result, types.Error):
        return None
    return result


async def is_user_banned(c: Client, chat_id: int, user_id: int) -> bool:
    member = await get_chat_member(c, chat_id, user_id)
    if not member:
        return False
    status = member.status
    return isinstance(status, types.ChatMemberStatusBanned)


async def is_user_restricted(c: Client, chat_id: int, user_id: int) -> bool:
    member = await get_chat_member(c, chat_id, user_id)
    if not member:
        return False
    return isinstance(member.status, types.ChatMemberStatusRestricted)


async def is_user_admin_in_chat(c: Client, chat_id: int, user_id: int) -> bool:
    member = await get_chat_member(c, chat_id, user_id)
    if not member:
        return False
    return isinstance(
        member.status,
        (types.ChatMemberStatusAdministrator, types.ChatMemberStatusCreator),
    )


async def get_admins(c: Client, chat_id: int) -> list:
    result = await c.searchChatMembers(
        chat_id=chat_id,
        filter=types.ChatMembersFilterAdministrators(),
    )
    if isinstance(result, types.Error):
        return []
    return result.members


async def get_user_name(c: Client, user_id: int) -> str:
    result = await c.getUser(user_id=user_id)
    if isinstance(result, types.Error):
        return str(user_id)
    name = result.first_name or ""
    if result.last_name:
        name += " " + result.last_name
    return name


async def get_user_mention(c: Client, user_id: int) -> str:
    name = await get_user_name(c, user_id)
    return f'<a href="tg://user?id={user_id}">{html.escape(name)}</a>'


async def get_chat_member_count(c: Client, chat_id: int) -> int:
    chat = await c.getChat(chat_id=chat_id)
    if isinstance(chat, types.Error):
        return 0
    if not isinstance(chat.type, types.ChatTypeSupergroup):
        return 0
    result = await c.getSupergroupFullInfo(supergroup_id=chat.type.supergroup_id)
    if isinstance(result, types.Error):
        return 0
    return result.member_count


async def get_chat_title(c: Client, chat_id: int) -> str:
    chat = await get_chat_info(c, chat_id)
    return chat.title if chat else "this chat"


async def get_reply_user(message: types.Message) -> Optional[int]:
    if not message.reply_to_message_id:
        return None
    result = await message.getRepliedMessage()
    if isinstance(result, types.Error):
        return None
    if result.sender_id and isinstance(result.sender_id, types.MessageSenderUser):
        return result.sender_id.user_id
    return None


async def send_video(
    c: Client, chat_id: int, video_path: str, caption: str = ""
) -> Union[types.Message, types.Error]:
    result = await c.sendDocument(
        chat_id=chat_id,
        document=types.InputFileLocal(path=video_path),
        caption=caption,
        parse_mode="html",
    )
    return result


async def send_photo(
    c: Client, chat_id: int, photo_path: str, caption: str = ""
) -> Union[types.Message, types.Error]:
    result = await c.sendPhoto(
        chat_id=chat_id,
        photo=types.InputFileLocal(path=photo_path),
        caption=caption,
        parse_mode="html",
    )
    return result
