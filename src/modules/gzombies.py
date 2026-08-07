#  Ported from LadyRezebb-reference/MukeshRobot/modules/zombies.py
#  Group management: Find and remove deleted/deactivated accounts

import asyncio

from pytdbot import Client, types

from src.core import Filter, DRAGONS, DEV_USERS, DEMONS, OWNER_ID
from src.core._admins import is_admin, load_admin_cache
from src.modules._helpers import ban_user, unban_user

__mod_name__ = "Zombie"
__help__ = """
<b>Remove deleted accounts:</b>
/zombies - Starts searching for deleted accounts in the group.
/zombies clean - Removes the deleted accounts from the group.
"""


OFFICERS = [OWNER_ID] + DEV_USERS + DRAGONS + DEMONS


async def _is_privileged(c: Client, chat_id: int, user_id: int) -> bool:
    if user_id in OFFICERS:
        return True
    return await is_admin(c, chat_id, user_id)


@Client.on_message(filters=Filter.command("zombies"))
async def zombies_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await _is_privileged(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    args = message.text.split(None, 1)
    clean_mode = len(args) >= 2 and args[1].strip().lower() == "clean"

    status_msg = await message.reply_text("Searching for deleted accounts...")

    del_count = 0
    admin_del_count = 0

    result = await c.searchChatMembers(
        chat_id=chat_id,
        query="",
        limit=200,
        filter=types.ChatMembersFilterMembers(),
    )
    if isinstance(result, types.Error):
        await status_msg.edit_text("Failed to search chat members.")
        return

    members = result.members
    deleted_ids = []

    for member in members:
        member_id = member.member_id
        if not hasattr(member_id, "user_id"):
            continue
            
        uid = member_id.user_id
        if uid == c.me.id:
            continue
            
        try:
            user_info = await c.getUser(user_id=uid)
            if not isinstance(user_info, types.Error):
                if isinstance(user_info.type, types.UserTypeDeleted):
                    del_count += 1
        except Exception:
            pass

    if not clean_mode:
        if del_count == 0:
            await status_msg.edit_text("Group clean, 0 deleted accounts found.")
        else:
            await status_msg.edit_text(
                f"Found <code>{del_count}</code> deleted accounts. "
                f"Use <code>/zombies clean</code> to remove them."
            )
        return

    removed = 0
    admin_skipped = 0

    for member in members:
        member_id = member.member_id
        if not hasattr(member_id, "user_id"):
            continue
        uid = member_id.user_id

        if uid == c.me.id:
            continue

        status = member.status
        is_creator = isinstance(status, types.ChatMemberStatusCreator)
        is_admin_member = isinstance(status, types.ChatMemberStatusAdministrator)

        if is_creator or is_admin_member:
            admin_skipped += 1
            continue

        user_info = await c.getUser(user_id=uid)
        if isinstance(user_info, types.Error):
            continue

        is_deleted = False
        if isinstance(user_info.type, types.UserTypeDeleted):
            is_deleted = True

        if is_deleted:
            success = await ban_user(c, chat_id, uid)
            if success:
                await unban_user(c, chat_id, uid)
                removed += 1
            await asyncio.sleep(0.5)

    if removed > 0:
        text = f"Cleaned <code>{removed}</code> zombies."
        if admin_skipped > 0:
            text += f"\n<code>{admin_skipped}</code> admin zombies not deleted."
        await status_msg.edit_text(text)
    else:
        await status_msg.edit_text("No deleted accounts found to clean.")
