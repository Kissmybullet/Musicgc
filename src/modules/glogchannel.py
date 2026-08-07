#  Ported from LadyRezebb-reference/MukeshRobot/modules/log_channel.py
#  Group management: Log channel settings

from pytdbot import Client, types

from src.core import Filter, group_db
from src.core._admins import is_admin

__mod_name__ = "Logs"
__help__ = """
<b>Admins only:</b>
/logchannel - Get log channel info
/setlog - Set the log channel
/unsetlog - Unset the log channel

Setting the log channel is done by:
1. Adding the bot to the desired channel (as an admin!)
2. Sending /setlog in the channel
3. Forwarding the /setlog to the group
"""


@Client.on_message(filters=Filter.command("logchannel"))
async def logchannel_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    log_channel = await group_db.get_log_channel(chat_id)
    if log_channel:
        channel_info = await c.getChat(chat_id=log_channel)
        if isinstance(channel_info, types.Error):
            await message.reply_text(
                f"Log channel is set to <code>{log_channel}</code> but I can't access it."
            )
        else:
            title = channel_info.title or str(log_channel)
            await message.reply_text(
                f"This group has all its logs sent to: <b>{title}</b> (<code>{log_channel}</code>)"
            )
    else:
        await message.reply_text("No log channel has been set for this group!")


@Client.on_message(filters=Filter.command("setlog"))
async def setlog_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    if not message.forward_info or not isinstance(
        message.forward_info.origin,
        (types.MessageOriginChat, types.MessageOriginChannel),
    ):
        await message.reply_text(
            "The steps to set a log channel are:\n"
            "- Add the bot to the desired channel (as an admin)\n"
            "- Send /setlog to the channel\n"
            "- Forward the /setlog to the group"
        )
        return

    if isinstance(message.forward_info.origin, types.MessageOriginChannel):
        log_channel_id = message.forward_info.origin.chat_id
    else:
        log_channel_id = message.forward_info.origin.sender_chat_id
    await group_db.set_log_channel(chat_id, log_channel_id)

    try:
        await c.sendTextMessage(
            chat_id=log_channel_id,
            text="This channel has been set as the log channel for this group.",
        )
    except Exception:
        pass

    await message.reply_text("Successfully set log channel!")


@Client.on_message(filters=Filter.command("unsetlog"))
async def unsetlog_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    log_channel = await group_db.get_log_channel(chat_id)
    if log_channel:
        await group_db.rm_log_channel(chat_id)
        try:
            chat_info = await c.getChat(chat_id=chat_id)
            chat_title = (
                chat_info.title
                if not isinstance(chat_info, types.Error)
                else "this group"
            )
            await c.sendTextMessage(
                chat_id=log_channel,
                text=f"Channel has been unlinked from {chat_title}.",
            )
        except Exception:
            pass
        await message.reply_text("Log channel has been un-set.")
    else:
        await message.reply_text("No log channel has been set yet!")
