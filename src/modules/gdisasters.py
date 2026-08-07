#  Ported from LadyRezebb-reference/MukeshRobot/modules/disasters.py
#  Manages special permission tiers (DRAGONS, DEMONS, TIGERS, WOLVES)
#  Only OWNER_ID can use these commands

import html

from pytdbot import Client, types

from src.core import (
    Filter,
    DRAGONS,
    DEV_USERS,
    DEMONS,
    TIGERS,
    WOLVES,
    OWNER_ID,
    SUPPORT_CHAT,
)
from src.modules._helpers import (
    get_reply_user,
    get_user_id,
    get_user_mention,
    get_user_name,
)

__mod_name__ = "Devs"
__help__ = """
<b>Notice:</b>
Commands listed here only work for users with special access. They are mainly
used for troubleshooting and debugging purposes. Group admins/owners do not need
these commands.

<b>List all special users:</b>
/sudolist - Lists all Dragon disasters
/supportlist - Lists all Demon disasters
/tigers - Lists all Tiger disasters
/wolves - Lists all Wolf disasters
/devlist - Lists all Hero Association members

<b>Owner only:</b>
/addsudo &lt;user&gt; - Adds a user to Dragon
/addsupport &lt;user&gt; - Adds a user to Demon
/addtiger &lt;user&gt; - Adds a user to Tiger
/addwolf &lt;user&gt; - Adds a user to Wolf
/rmsudo &lt;user&gt; - Removes a user from Dragon
/rmsupport &lt;user&gt; - Removes a user from Demon
/rmtiger &lt;user&gt; - Removes a user from Tiger
/rmwolf &lt;user&gt; - Removes a user from Wolf
"""


async def _resolve_target(c: Client, message: types.Message) -> tuple:
    """Resolve target user from reply or args."""
    target_id = await get_reply_user(message)
    args = message.text.split(None, 1)
    if not target_id and len(args) >= 2:
        target_id = await get_user_id(c, args[1])
    return target_id


async def _check_target(
    c: Client, message: types.Message, target_id: int
) -> str | None:
    """Validate target user. Returns error message or None if ok."""
    if not target_id:
        return "Please reply to a user or provide a user ID/username."
    if target_id == c.me.id:
        return "This does not work that way."
    return None


def _list_users(user_ids: list, exclude: set = None) -> str:
    """Build a mention list from user IDs."""
    if exclude:
        user_ids = [uid for uid in user_ids if uid not in exclude]
    lines = []
    for uid in user_ids:
        lines.append(f"- <a href='tg://user?id={uid}'>{uid}</a>")
    return "\n".join(lines) if lines else "None"


@Client.on_message(filters=Filter.command("addsudo"))
async def addsudo_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS:
        await message.reply_text("Only the bot owner can use this command.")
        return

    target_id = await _resolve_target(c, message)
    err = await _check_target(c, message, target_id)
    if err:
        await message.reply_text(err)
        return

    if target_id in DRAGONS:
        await message.reply_text("This member is already a Dragon Disaster.")
        return

    if target_id in DEMONS:
        DEMONS.remove(target_id)
    if target_id in WOLVES:
        WOLVES.remove(target_id)
    if target_id in TIGERS:
        TIGERS.remove(target_id)

    DRAGONS.append(target_id)
    name = await get_user_name(c, target_id)
    await message.reply_text(f"Successfully set Disaster level of {name} to Dragon!")


@Client.on_message(filters=Filter.command(["rmsudo", "removesudo"]))
async def rmsudo_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS:
        await message.reply_text("Only the bot owner can use this command.")
        return

    target_id = await _resolve_target(c, message)
    err = await _check_target(c, message, target_id)
    if err:
        await message.reply_text(err)
        return

    if target_id in DRAGONS:
        DRAGONS.remove(target_id)
        name = await get_user_name(c, target_id)
        await message.reply_text(f"Requested to demote {name} to Civilian.")
    else:
        await message.reply_text("This user is not a Dragon Disaster!")


@Client.on_message(filters=Filter.command(["addsupport", "adddemon"]))
async def addsupport_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS and user_id not in DRAGONS:
        await message.reply_text("Only the bot owner/Dev can use this command.")
        return

    target_id = await _resolve_target(c, message)
    err = await _check_target(c, message, target_id)
    if err:
        await message.reply_text(err)
        return

    if target_id in DEMONS:
        await message.reply_text("This user is already a Demon Disaster.")
        return

    if target_id in DRAGONS:
        DRAGONS.remove(target_id)
    if target_id in WOLVES:
        WOLVES.remove(target_id)

    DEMONS.append(target_id)
    name = await get_user_name(c, target_id)
    await message.reply_text(f"{name} was added as a Demon Disaster!")


@Client.on_message(
    filters=Filter.command(["rmsupport", "removesupport", "removedemon"])
)
async def rmsupport_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS and user_id not in DRAGONS:
        await message.reply_text("Only the bot owner/Dev can use this command.")
        return

    target_id = await _resolve_target(c, message)
    err = await _check_target(c, message, target_id)
    if err:
        await message.reply_text(err)
        return

    if target_id in DEMONS:
        DEMONS.remove(target_id)
        name = await get_user_name(c, target_id)
        await message.reply_text(f"Demoted {name} to Civilian.")
    else:
        await message.reply_text("This user is not a Demon level Disaster!")


@Client.on_message(filters=Filter.command("addtiger"))
async def addtiger_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS and user_id not in DRAGONS:
        await message.reply_text("Only the bot owner/Dev can use this command.")
        return

    target_id = await _resolve_target(c, message)
    err = await _check_target(c, message, target_id)
    if err:
        await message.reply_text(err)
        return

    if target_id in TIGERS:
        await message.reply_text("This user is already a Tiger Disaster.")
        return

    if target_id in DRAGONS:
        DRAGONS.remove(target_id)
    if target_id in DEMONS:
        DEMONS.remove(target_id)
    if target_id in WOLVES:
        WOLVES.remove(target_id)

    TIGERS.append(target_id)
    name = await get_user_name(c, target_id)
    await message.reply_text(f"Successfully promoted {name} to a Tiger Disaster!")


@Client.on_message(filters=Filter.command(["rmtiger", "removetiger"]))
async def rmtiger_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS and user_id not in DRAGONS:
        await message.reply_text("Only the bot owner/Dev can use this command.")
        return

    target_id = await _resolve_target(c, message)
    err = await _check_target(c, message, target_id)
    if err:
        await message.reply_text(err)
        return

    if target_id in TIGERS:
        TIGERS.remove(target_id)
        await message.reply_text("Demoted to normal user.")
    else:
        await message.reply_text("This user is not a Tiger Disaster!")


@Client.on_message(filters=Filter.command(["addwolf", "addwhitelist"]))
async def addwolf_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS and user_id not in DRAGONS:
        await message.reply_text("Only the bot owner/Dev can use this command.")
        return

    target_id = await _resolve_target(c, message)
    err = await _check_target(c, message, target_id)
    if err:
        await message.reply_text(err)
        return

    if target_id in WOLVES:
        await message.reply_text("This user is already a Wolf Disaster.")
        return

    if target_id in DRAGONS:
        DRAGONS.remove(target_id)
    if target_id in DEMONS:
        DEMONS.remove(target_id)
    if target_id in TIGERS:
        TIGERS.remove(target_id)

    WOLVES.append(target_id)
    name = await get_user_name(c, target_id)
    await message.reply_text(f"Successfully promoted {name} to a Wolf Disaster!")


@Client.on_message(filters=Filter.command(["rmwolf", "removewolf", "removewhitelist"]))
async def rmwolf_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    if user_id != OWNER_ID and user_id not in DEV_USERS and user_id not in DRAGONS:
        await message.reply_text("Only the bot owner/Dev can use this command.")
        return

    target_id = await _resolve_target(c, message)
    err = await _check_target(c, message, target_id)
    if err:
        await message.reply_text(err)
        return

    if target_id in WOLVES:
        WOLVES.remove(target_id)
        await message.reply_text("Demoted to normal user.")
    else:
        await message.reply_text("This user is not a Wolf Disaster!")


@Client.on_message(filters=Filter.command("sudolist"))
async def sudolist_cmd(c: Client, message: types.Message):
    true_sudo = [uid for uid in DRAGONS if uid not in DEV_USERS]
    text = "<b>Known Dragon Disasters:</b>\n" + _list_users(true_sudo)
    await message.reply_text(text)


@Client.on_message(filters=Filter.command("supportlist"))
async def supportlist_cmd(c: Client, message: types.Message):
    text = "<b>Known Demon Disasters:</b>\n" + _list_users(DEMONS)
    await message.reply_text(text)


@Client.on_message(filters=Filter.command("tigers"))
async def tigers_cmd(c: Client, message: types.Message):
    text = "<b>Known Tiger Disasters:</b>\n" + _list_users(TIGERS)
    await message.reply_text(text)


@Client.on_message(filters=Filter.command("wolves"))
async def wolves_cmd(c: Client, message: types.Message):
    text = "<b>Known Wolf Disasters:</b>\n" + _list_users(WOLVES)
    await message.reply_text(text)


@Client.on_message(filters=Filter.command("devlist"))
async def devlist_cmd(c: Client, message: types.Message):
    true_dev = [uid for uid in DEV_USERS if uid != OWNER_ID]
    text = "<b>Dev Users:</b>\n" + _list_users(true_dev)
    await message.reply_text(text)
