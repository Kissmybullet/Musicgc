#  Ported from LadyRezebb-reference/MukeshRobot/modules/tagall.py
#  Group management: Tag/mention all members

import asyncio
import html

from pytdbot import Client, types

from src.core import Filter
from src.core._admins import load_admin_cache
from src.modules._helpers import get_user_mention

__mod_name__ = "Tagall"
__help__ = """
<b>Only for admins:</b>
/tagall &lt;text&gt; or reply to a message - Mention all members in your group.
/all &lt;text&gt; - Same as /tagall
"""

spam_chats: list[int] = []


async def _get_group_members(c: Client, chat_id: int) -> list[types.ChatMember]:
    chat = await c.getChat(chat_id=chat_id)
    if isinstance(chat, types.Error):
        return []

    members: list[types.ChatMember] = []
    offset = 0

    if isinstance(chat.type, types.ChatTypeSupergroup):
        while True:
            result = await c.getSupergroupMembers(
                supergroup_id=chat.type.supergroup_id,
                filter=types.SupergroupMembersFilterMembers(),
                offset=offset,
                limit=200,
            )
            if isinstance(result, types.Error):
                break

            page_members = result.members
            if not page_members:
                break

            members.extend(page_members)
            offset += len(page_members)

            if len(page_members) < 200:
                break

        return members

    result = await c.searchChatMembers(
        chat_id=chat_id,
        query="",
        limit=200,
        filter=types.ChatMembersFilterMembers(),
    )
    if isinstance(result, types.Error):
        return []
    return list(result.members)


async def _send_tag_batch(
    c: Client,
    chat_id: int,
    message_text: str,
    mentions: list[str],
    reply_to_message_id: int = 0,
) -> None:
    if not mentions:
        return

    payload = ", ".join(mentions)
    if message_text:
        payload = f"{html.escape(message_text)}\n{payload}"

    kwargs = {
        "chat_id": chat_id,
        "text": payload,
        "parse_mode": "html",
    }
    if reply_to_message_id:
        kwargs["reply_to_message_id"] = reply_to_message_id

    await c.sendTextMessage(**kwargs)


@Client.on_message(filters=Filter.command(["tagall", "all", "mentionall"]))
async def tagall_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command can only be used in groups!")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("Failed to verify admin status.")
        return

    from src.core._admins import is_admin

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("Only admins can mention all!")
        return

    args = message.text.split(None, 1)
    has_text = len(args) >= 2
    is_reply = bool(message.reply_to_message_id)

    if has_text and is_reply:
        await message.reply_text(
            "Give me one argument! (either text or reply, not both)"
        )
        return
    elif has_text:
        msg_text = args[1]
    elif is_reply:
        replied = await message.getRepliedMessage()
        if isinstance(replied, types.Error) or not hasattr(replied, "content"):
            await message.reply_text("I can't mention members for older messages!")
            return
        if hasattr(replied.content, "text"):
            msg_text = replied.content.text.text
        else:
            await message.reply_text("The replied message has no text.")
            return
    else:
        await message.reply_text(
            "Reply to a message or give me some text to mention others!"
        )
        return

    spam_chats.append(chat_id)

    try:
        members = await _get_group_members(c, chat_id)
        mentions: list[str] = []

        for member in members:
            if chat_id not in spam_chats:
                break

            member_id = member.member_id
            if not isinstance(member_id, types.MessageSenderUser):
                continue

            uid = member_id.user_id
            if uid == c.me.id:
                continue

            try:
                user_info = await c.getUser(user_id=uid)
                if isinstance(user_info, types.Error):
                    continue
                if getattr(user_info, "type", None) and type(user_info.type).__name__ == "UserTypeBot":
                    continue
            except Exception:
                continue

            mentions.append(await get_user_mention(c, uid))

            if len(mentions) == 10:
                await _send_tag_batch(
                    c,
                    chat_id,
                    msg_text if has_text else "",
                    mentions,
                    message.reply_to_message_id if is_reply else 0,
                )
                await asyncio.sleep(3)
                mentions = []

        if mentions:
            await _send_tag_batch(
                c,
                chat_id,
                msg_text if has_text else "",
                mentions,
                message.reply_to_message_id if is_reply else 0,
            )
    finally:
        try:
            spam_chats.remove(chat_id)
        except ValueError:
            pass
