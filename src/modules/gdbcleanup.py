#  Ported from LadyRezebb-reference/MukeshRobot/modules/dbcleanup.py
#  Database cleanup: remove stale chats and gbanned users

import asyncio

from pytdbot import Client, types

from src.core import DEV_USERS, OWNER_ID, Filter, db

__mod_name__ = "DatabaseCleanup"
__help__ = """
<b>Database Cleanup Commands (owner only):</b>
/dbclean - Scan and remove stale entries from the database
"""


@Client.on_message(filters=Filter.command("dbclean"))
async def dbclean_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS:
        await message.reply_text("Only the owner can use this command.")
        return

    status_msg = await message.reply_text("Starting database cleanup...")

    chats = await db.get_all_chats()
    total_chats = len(chats)
    removed_chats = 0

    users = await db.get_all_users()
    total_users = len(users)
    removed_users = 0

    if total_chats > 0:
        await status_msg.edit_text(
            f"Checking {total_chats} chats... (this may take a while)"
        )
        for chat_id in chats:
            await asyncio.sleep(0.1)
            try:
                result = await c.getChat(chat_id=chat_id)
                if isinstance(result, types.Error):
                    await db.remove_chat(chat_id)
                    removed_chats += 1
            except Exception:
                await db.remove_chat(chat_id)
                removed_chats += 1

    if total_users > 0:
        await status_msg.edit_text(
            f"Checking {total_users} users... (this may take a while)"
        )
        for uid in users:
            await asyncio.sleep(0.1)
            try:
                result = await c.getUser(user_id=uid)
                if isinstance(result, types.Error):
                    await db.remove_user(uid)
                    removed_users += 1
            except Exception:
                await db.remove_user(uid)
                removed_users += 1

    await status_msg.edit_text(
        f"<b>Database Cleanup Complete</b>\n\n"
        f"Chats scanned: <code>{total_chats}</code>\n"
        f"Chats removed: <code>{removed_chats}</code>\n\n"
        f"Users scanned: <code>{total_users}</code>\n"
        f"Users removed: <code>{removed_users}</code>"
    )
