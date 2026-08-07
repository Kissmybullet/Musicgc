#  Ported from LadyRezebb-reference/MukeshRobot/modules/fsub.py
#  Group management: Force subscribe to a channel

from pytdbot import Client, types

from src.core import Filter, group_db, DRAGONS, OWNER_ID
from src.core._admins import is_admin, is_owner, load_admin_cache

__mod_name__ = "F-Sub"
__help__ = """
<b>Force Subscribe:</b>
The bot can mute members who are not subscribed to your channel until they subscribe.

<b>Setup:</b>
1. Add the bot to your group as admin
2. Add the bot to your channel as admin

<b>Commands:</b>
/fsub &lt;channel&gt; - Turn on and set up force subscribe
/fsub - Check current force subscribe status
/fsuboff - Turn off force subscribe
"""


@Client.on_message(filters=Filter.command("fsub"))
async def fsub_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    is_chat_owner = await is_owner(c, chat_id, user_id)
    is_chat_admin = await is_admin(c, chat_id, user_id)
    if not is_chat_admin:
        await message.reply_text("You need to be an admin to do this.")
        return
    if not is_chat_owner and user_id not in DRAGONS and user_id != OWNER_ID:
        await message.reply_text(
            "You need to be the group creator to set force subscribe."
        )
        return

    args = message.text.split(None, 1)
    channel = args[1].strip() if len(args) >= 2 else None

    if not channel:
        fsub = await group_db.get_fsub(chat_id)
        if not fsub:
            await message.reply_text("Force subscribe is disabled in this chat.")
        else:
            await message.reply_text(
                f"Force subscribe is currently <b>enabled</b>. "
                f"Users are forced to join <b>@{fsub}</b> to speak here."
            )
        return

    if channel.lower() in ("off", "no", "n"):
        await group_db.rm_fsub(chat_id)
        await message.reply_text("Force subscribe has been disabled successfully.")
        return

    channel_name = channel.lstrip("@")

    try:
        channel_chat = await c.searchPublicChat(username=channel_name)
        if isinstance(channel_chat, types.Error):
            await message.reply_text("Invalid channel username provided.")
            return

        if not hasattr(channel_chat, "type") or channel_chat.type not in (
            "chatTypeSupergroup",
            "chatTypeChannel",
        ):
            await message.reply_text("That's not a valid channel.")
            return
    except Exception:
        await message.reply_text("Invalid channel username provided.")
        return

    await group_db.set_fsub(chat_id, channel_name)
    await message.reply_text(f"Force subscribe is <b>enabled</b> to @{channel_name}.")


@Client.on_message(filters=Filter.command("fsuboff"))
async def fsuboff_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    is_chat_owner = await is_owner(c, chat_id, user_id)
    is_chat_admin = await is_admin(c, chat_id, user_id)
    if not is_chat_admin:
        await message.reply_text("You need to be an admin to do this.")
        return
    if not is_chat_owner and user_id not in DRAGONS and user_id != OWNER_ID:
        await message.reply_text(
            "You need to be the group creator to disable force subscribe."
        )
        return

    fsub = await group_db.get_fsub(chat_id)
    if not fsub:
        await message.reply_text("Force subscribe is already disabled.")
        return

    await group_db.rm_fsub(chat_id)
    await message.reply_text("Force subscribe has been disabled successfully.")
