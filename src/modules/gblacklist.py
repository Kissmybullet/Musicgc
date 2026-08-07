#  Ported from LadyRezebb-reference/MukeshRobot/modules/blacklist.py
#  Group management: Blacklist words, auto-delete messages, bluelist

import html
import re

from pytdbot import Client, types

from src.core import Filter, group_db
from src.core._admins import is_admin, load_admin_cache
from src.modules._helpers import (
    ban_user,
    delete_message,
    get_chat_title,
    get_reply_user,
    get_user_id,
    get_user_mention,
    is_user_admin_in_chat,
    kick_user,
    mute_user,
    send_message,
)

__mod_name__ = "Blacklist"
__help__ = """
<b>Blacklist Commands:</b>
/blacklist - View current blacklisted words
/addblacklist &lt;words&gt; - Add words to blacklist (one per line)
/unblacklist &lt;words&gt; - Remove words from blacklist
/unblacklistall - Remove all blacklisted words
/bluelist - List all users with blue checkmarks (premium)
"""


@Client.on_message(filters=Filter.command("blacklist"))
async def blacklist_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    words = await group_db.get_blacklist(chat_id)

    if not words:
        await message.reply_text(
            f"No blacklisted words in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
        )
        return

    text = f"Current blacklisted words in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>:\n\n"
    for word in words:
        text += f"  • <code>{html.escape(word)}</code>\n"

    await message.reply_text(text)


@Client.on_message(filters=Filter.command("addblacklist"))
async def add_blacklist_cmd(c: Client, message: types.Message):
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
            "Tell me which words you would like to add to the blacklist."
        )
        return

    text = args[1]
    to_blacklist = list(
        {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
    )

    for trigger in to_blacklist:
        await group_db.add_blacklist(chat_id, trigger.lower())

    if len(to_blacklist) == 1:
        await message.reply_text(
            f"Added blacklist <code>{html.escape(to_blacklist[0])}</code> "
            f"in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
        )
    else:
        await message.reply_text(
            f"Added <b>{len(to_blacklist)}</b> blacklist triggers "
            f"in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
        )


@Client.on_message(filters=Filter.command("unblacklist"))
async def unblacklist_cmd(c: Client, message: types.Message):
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
            "Tell me which words you would like to remove from the blacklist!"
        )
        return

    text = args[1]
    to_unblacklist = list(
        {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
    )
    current_words = await group_db.get_blacklist(chat_id)
    successful = 0

    for trigger in to_unblacklist:
        if trigger.lower() in [w.lower() for w in current_words]:
            await group_db.rm_blacklist(chat_id, trigger.lower())
            successful += 1

    if len(to_unblacklist) == 1:
        if successful:
            await message.reply_text(
                f"Removed <code>{html.escape(to_unblacklist[0])}</code> from blacklist "
                f"in <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
            )
        else:
            await message.reply_text("That's not a blacklisted word!")
    elif successful == len(to_unblacklist):
        await message.reply_text(
            f"Removed <b>{successful}</b> words from blacklist in "
            f"<b>{html.escape(await get_chat_title(c, message.chat_id))}</b>!"
        )
    elif not successful:
        await message.reply_text("None of these are blacklisted words.")
    else:
        await message.reply_text(
            f"Removed <b>{successful}</b> words. "
            f"<b>{len(to_unblacklist) - successful}</b> did not exist."
        )


@Client.on_message(filters=Filter.command("unblacklistall"))
async def unblacklist_all_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    words = await group_db.get_blacklist(chat_id)
    if not words:
        await message.reply_text("There are no blacklisted words in this chat.")
        return

    await group_db.rm_all_blacklist(chat_id)
    await message.reply_text("Successfully cleared all blacklisted words!")


@Client.on_message(filters=Filter.command("bluelist"))
async def bluelist_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    result = await c.searchChatMembers(
        chat_id=chat_id,
        filter=types.ChatMembersFilterMembers(),
    )

    if isinstance(result, types.Error):
        await message.reply_text("Failed to fetch chat members.")
        return

    text = f"<b>Members with Blue Checkmarks in {html.escape(await get_chat_title(c, message.chat_id))}:</b>\n\n"
    count = 0

    for member in result.members:
        member_id = member.member_id
        if not isinstance(member_id, types.MessageSenderUser):
            continue

        uid = member_id.user_id
        user_result = await c.getUser(user_id=uid)
        if isinstance(user_result, types.Error):
            continue

        if user_result.premium_gift_options:
            name = await get_user_mention(c, uid)
            text += f"  • {name}\n"
            count += 1

    if count == 0:
        await message.reply_text("No members with blue checkmarks found.")
    else:
        await message.reply_text(text)


@Client.on_updateNewMessage(filters=Filter.regex(r"(?i).+"))
async def blacklist_watcher(c: Client, update: types.UpdateNewMessage):
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

    if not isinstance(message.content, types.MessageText):
        return

    text = message.content.text.text
    if not text:
        return

    blacklist_words = await group_db.get_blacklist(chat_id)
    if not blacklist_words:
        return

    for trigger in blacklist_words:
        pattern = r"(?:^|[\s\b])" + re.escape(trigger) + r"(?:$|[\s\b])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            await delete_message(c, chat_id, message.id)
            break
