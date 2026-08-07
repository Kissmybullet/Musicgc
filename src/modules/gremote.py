#  Ported from LadyRezebb-reference/MukeshRobot/modules/remote_cmds.py
#  Remote moderation: Ban, Unban, Kick, Mute, Unmute in specified chats

from pytdbot import Client, types

from src.core import DEV_USERS, OWNER_ID, Filter
from src.core._admins import load_admin_cache
from src.modules._helpers import (
    ban_user,
    get_user_id,
    get_user_mention,
    is_user_admin_in_chat,
    mute_user,
    send_message,
    unban_user,
    unmute_user,
)

__mod_name__ = "Remote"
__help__ = """
<b>Remote Commands (devs only):</b>
/rban &lt;chat_id&gt; &lt;user&gt; - Ban user in specified chat
/runban &lt;chat_id&gt; &lt;user&gt; - Unban user in specified chat
/rkick &lt;chat_id&gt; &lt;user&gt; - Kick user in specified chat
/rmute &lt;chat_id&gt; &lt;user&gt; - Mute user in specified chat
/runmute &lt;chat_id&gt; &lt;user&gt; - Unmute user in specified chat
"""


def _is_dev(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in DEV_USERS


async def _parse_remote_args_simple(c: Client, message: types.Message):
    """Parse: /cmd <chat_id> <user>"""
    args = message.text.split(None, 2)
    if len(args) < 3:
        return None, None, ("You don't seem to be referring to a chat/user.")

    try:
        target_chat_id = int(args[1])
    except ValueError:
        target_chat_id = await get_user_id(c, args[1])
        if target_chat_id is None:
            return None, None, "Invalid chat ID specified."

    target_user_id = await get_reply_or_arg_user(c, message, args)
    if target_user_id is None:
        return (
            None,
            None,
            "You don't seem to be referring to a user or the ID specified is incorrect.",
        )

    return target_chat_id, target_user_id, None


async def get_reply_or_arg_user(c: Client, message: types.Message, args: list):
    """Get user from reply or argument."""
    from src.modules._helpers import get_reply_user

    target_id = await get_reply_user(message)
    if not target_id and len(args) >= 3:
        target_id = await get_user_id(c, args[2])
    elif not target_id and len(args) >= 2:
        # Try args[1] if chat_id was from reply
        pass
    return target_id


@Client.on_message(filters=Filter.command("rban"))
async def rban_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if not _is_dev(user_id):
        await message.reply_text("Only developers can use this command.")
        return

    target_chat_id, target_user_id, err = await _parse_remote_args_simple(c, message)
    if err:
        await message.reply_text(err)
        return

    if target_user_id == c.me.id:
        await message.reply_text("I'm not going to ban myself.")
        return

    if await is_user_admin_in_chat(c, target_chat_id, target_user_id):
        await message.reply_text("I really wish I could ban admins...")
        return

    success = await ban_user(c, target_chat_id, target_user_id)
    if success:
        name = await get_user_mention(c, target_user_id)
        await message.reply_text(
            f"Banned {name} from chat <code>{target_chat_id}</code>."
        )
    else:
        await message.reply_text(
            "Failed to ban. Make sure I'm admin there and can ban users."
        )


@Client.on_message(filters=Filter.command("runban"))
async def runban_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if not _is_dev(user_id):
        await message.reply_text("Only developers can use this command.")
        return

    target_chat_id, target_user_id, err = await _parse_remote_args_simple(c, message)
    if err:
        await message.reply_text(err)
        return

    if target_user_id == c.me.id:
        await message.reply_text("I'm not going to unban myself.")
        return

    success = await unban_user(c, target_chat_id, target_user_id)
    if success:
        name = await get_user_mention(c, target_user_id)
        await message.reply_text(
            f"Unbanned {name} from chat <code>{target_chat_id}</code>."
        )
    else:
        await message.reply_text("Failed to unban. Make sure I'm admin there.")


@Client.on_message(filters=Filter.command("rkick"))
async def rkick_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if not _is_dev(user_id):
        await message.reply_text("Only developers can use this command.")
        return

    target_chat_id, target_user_id, err = await _parse_remote_args_simple(c, message)
    if err:
        await message.reply_text(err)
        return

    if target_user_id == c.me.id:
        await message.reply_text("I'm not going to kick myself.")
        return

    if await is_user_admin_in_chat(c, target_chat_id, target_user_id):
        await message.reply_text("I really wish I could kick admins...")
        return

    from src.modules._helpers import kick_user

    success = await kick_user(c, target_chat_id, target_user_id)
    if success:
        name = await get_user_mention(c, target_user_id)
        await message.reply_text(
            f"Kicked {name} from chat <code>{target_chat_id}</code>."
        )
    else:
        await message.reply_text("Failed to kick. Make sure I'm admin there.")


@Client.on_message(filters=Filter.command("rmute"))
async def rmute_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if not _is_dev(user_id):
        await message.reply_text("Only developers can use this command.")
        return

    target_chat_id, target_user_id, err = await _parse_remote_args_simple(c, message)
    if err:
        await message.reply_text(err)
        return

    if target_user_id == c.me.id:
        await message.reply_text("I'm not going to mute myself.")
        return

    if await is_user_admin_in_chat(c, target_chat_id, target_user_id):
        await message.reply_text("I really wish I could mute admins...")
        return

    success = await mute_user(c, target_chat_id, target_user_id)
    if success:
        name = await get_user_mention(c, target_user_id)
        await message.reply_text(f"Muted {name} in chat <code>{target_chat_id}</code>.")
    else:
        await message.reply_text("Failed to mute. Make sure I'm admin there.")


@Client.on_message(filters=Filter.command("runmute"))
async def runmute_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if not _is_dev(user_id):
        await message.reply_text("Only developers can use this command.")
        return

    target_chat_id, target_user_id, err = await _parse_remote_args_simple(c, message)
    if err:
        await message.reply_text(err)
        return

    if target_user_id == c.me.id:
        await message.reply_text("I'm not going to unmute myself.")
        return

    success = await unmute_user(c, target_chat_id, target_user_id)
    if success:
        name = await get_user_mention(c, target_user_id)
        await message.reply_text(
            f"Unmuted {name} in chat <code>{target_chat_id}</code>."
        )
    else:
        await message.reply_text("Failed to unmute. Make sure I'm admin there.")
