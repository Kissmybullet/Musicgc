#  Ported from LadyRezebb-reference/MukeshRobot/modules/couples.py
#  Pick a random couple from chat members

import random
from datetime import datetime

from pytdbot import Client, types

from src.core import Filter, group_db

__mod_name__ = "Couples"
__help__ = """
<b>Couples Commands:</b>
/couples - Pick a random couple from the chat

Picks two random non-bot members and pairs them as today's couple.
The result is cached per day so you get the same couple until midnight.
"""


def _today_str() -> str:
    return datetime.now().strftime("%d/%m/%Y")


@Client.on_message(filters=Filter.command("couples"))
async def couples_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    today = _today_str()

    existing = await group_db.get_couple(chat_id, today)
    if existing:
        c1_id = existing.get("c1_id")
        c2_id = existing.get("c2_id")
        name1 = await _get_name(c, c1_id)
        name2 = await _get_name(c, c2_id)
        await message.reply_text(
            f"<b>Today's couple:</b>\n\n"
            f"❤️ {name1} ❤️ {name2} ❤️\n\n"
            f"<i>Next couple will be selected tomorrow!</i>"
        )
        return

    status_msg = await message.reply_text("Generating couples, please wait...")

    result = await c.searchChatMembers(
        chat_id=chat_id,
        filter=types.ChatMembersFilterMembers(),
        limit=100,
    )

    if isinstance(result, types.Error):
        await status_msg.edit_text("Failed to fetch chat members.")
        return

    user_ids = []
    for member in result.members:
        member_id = member.member_id
        if isinstance(member_id, types.MessageSenderUser):
            uid = member_id.user_id
            if uid != c.me.id:
                user_result = await c.getUser(user_id=uid)
                if isinstance(user_result, types.Error):
                    continue
                if (
                    not getattr(user_result, "type", None)
                    or type(user_result.type).__name__ != "UserTypeBot"
                ):
                    user_ids.append(uid)

    if len(user_ids) < 2:
        await status_msg.edit_text("Not enough members to pick a couple.")
        return

    c1_id = random.choice(user_ids)
    c2_id = random.choice(user_ids)
    attempts = 0
    while c2_id == c1_id and attempts < 50:
        c2_id = random.choice(user_ids)
        attempts += 1

    await group_db.set_couple(chat_id, today, {"c1_id": c1_id, "c2_id": c2_id})

    name1 = await _get_name(c, c1_id)
    name2 = await _get_name(c, c2_id)

    await status_msg.edit_text(
        f"<b>Today's couple:</b>\n\n"
        f"❤️ {name1} ❤️ {name2} ❤️\n\n"
        f"<i>Next couple will be selected tomorrow!</i>"
    )


async def _get_name(c: Client, user_id: int) -> str:
    result = await c.getUser(user_id=user_id)
    if isinstance(result, types.Error):
        return str(user_id)
    name = result.first_name or ""
    if result.last_name:
        name += " " + result.last_name
    return f'<a href="tg://user?id={user_id}">{name}</a>'
