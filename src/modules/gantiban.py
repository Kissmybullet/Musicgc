#  Ported from LadyRezebb-reference/MukeshRobot/modules/antiban.py
#  Anti-channel: auto-delete channel posts in groups and ban the channel

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "AntiBan"
__help__ = """
<b>Anti-Channel (automatic):</b>
Automatically deletes messages posted by channels in groups and bans the channel.
No commands needed - this runs as a background watcher.
"""


@Client.on_updateNewMessage(position=0)
async def antiban_watcher(c: Client, update: types.UpdateNewMessage):
    message = update.message
    if not message:
        return

    chat_id = message.chat_id
    if chat_id > 0:
        return

    sender = message.sender_id
    if not sender or not isinstance(sender, types.MessageSenderChat):
        return

    channel_id = sender.chat_id
    if channel_id == chat_id:
        return

    await c.deleteMessages(chat_id=chat_id, message_ids=[message.id])
    await c.banChatMember(
        chat_id=chat_id,
        member_id=types.MessageSenderChat(chat_id=channel_id),
    )
    await c.sendTextMessage(
        chat_id=chat_id,
        text=(
            f"#ANTICHANNEL\n\n"
            f"\u2b6d Sender ID: <code>{channel_id}</code>\n"
            f"\u2b6d Action Taken: <b>DELETE &amp; BAN</b>"
        ),
        disable_web_page_preview=True,
    )
