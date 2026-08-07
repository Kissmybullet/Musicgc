#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import asyncio

from pytdbot import Client, types

from src.core import Filter
from src.core._admins import admins_only
from src.modules._helpers import edit_message, unban_user

__mod_name__ = "UnbanAll"
__help__ = """
<b>UnbanAll Commands:</b>
/unbanall - Removes bans for all previously banned users in the current group.
"""


@Client.on_message(filters=Filter.command(["unbanall"]))
@admins_only(permissions="can_restrict_members")
async def unbanall_cmd(c: Client, message: types.Message):
    """Unbans all members in a chat."""
    chat_id = message.chat_id

    if chat_id > 0:
        await message.reply_text("This command can only be used in groups.")
        return

    chat = await c.getChat(chat_id=chat_id)
    if isinstance(chat, types.Error):
        await message.reply_text("Failed to fetch chat info.")
        return

    if not isinstance(chat.type, types.ChatTypeSupergroup):
        await message.reply_text("Cannot unban all in this type of chat.")
        return

    msg = await message.reply_text("Fetching banned users...")

    try:
        count = 0
        offset = 0
        while True:
            result = await c.getSupergroupMembers(
                supergroup_id=chat.type.supergroup_id,
                filter=types.SupergroupMembersFilterBanned(),
                offset=offset,
                limit=200,
            )
            if isinstance(result, types.Error):
                break

            members = result.members
            if not members:
                break

            for member in members:
                member_id = member.member_id
                if isinstance(member_id, types.MessageSenderUser):
                    user_id = member_id.user_id
                    await unban_user(c, chat_id, user_id)
                    count += 1
                    await asyncio.sleep(0.5)

            offset += len(members)
            if len(members) < 200:
                break

        await edit_message(c, chat_id, msg.id, f"Successfully unbanned {count} users!")

    except Exception as e:
        await edit_message(c, chat_id, msg.id, f"An error occurred: {str(e)}")
