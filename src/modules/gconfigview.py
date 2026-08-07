import html

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core._config import config
from src.core._admins import is_admin

__mod_name__ = "Config View"
__help__ = """
<b>Config Commands:</b>
/config - View current bot configuration.
/config <var> - View a specific config variable.

<b>Available variables:</b>
API_ID, OWNER_ID, LOGGER_ID, DEFAULT_SERVICE, MAX_FILE_SIZE,
SUPPORT_GROUP, SUPPORT_CHANNEL, DB_NAME, AUTO_LEAVE, NO_UPDATES
"""

_SENSITIVE_VARS = {"API_HASH", "TOKEN", "MONGO_URI", "SESSION_STRINGS", "PROXY"}


@Client.on_message(filters=Filter.command("configview"))
async def configview_cmd(c: Client, message: Message):
    user_id = message.from_id
    chat_id = message.chat_id

    if not await is_admin(c, chat_id, user_id):
        return await message.reply_text("You need to be an admin to view config.")

    args = message.text.split()
    if len(args) >= 2:
        var_name = args[1].upper()
        if var_name in _SENSITIVE_VARS:
            return await message.reply_text(
                f"<code>{var_name}</code> is a sensitive variable and cannot be displayed."
            )
        value = getattr(config, var_name, None)
        if value is None:
            return await message.reply_text(
                f"Variable <code>{var_name}</code> not found."
            )
        return await message.reply_text(
            f"<b>{html.escape(var_name)}:</b>\n<code>{html.escape(str(value))}</code>"
        )

    config_lines = []
    display_vars = [
        ("OWNER_ID", config.OWNER_ID),
        ("LOGGER_ID", config.LOGGER_ID),
        ("DEFAULT_SERVICE", config.DEFAULT_SERVICE),
        ("MAX_FILE_SIZE", f"{config.MAX_FILE_SIZE // (1024 * 1024)} MB"),
        ("SUPPORT_GROUP", config.SUPPORT_GROUP),
        ("SUPPORT_CHANNEL", config.SUPPORT_CHANNEL),
        ("DB_NAME", config.DB_NAME),
        ("AUTO_LEAVE", config.AUTO_LEAVE),
        ("NO_UPDATES", config.NO_UPDATES),
        ("MIN_MEMBER_COUNT", config.MIN_MEMBER_COUNT),
        ("DEVS", config.DEVS),
    ]
    for name, value in display_vars:
        config_lines.append(f"  <b>{name}:</b> <code>{html.escape(str(value))}</code>")

    text = (
        "<b>Bot Configuration:</b>\n\n"
        + "\n".join(config_lines)
        + "\n\n<i>Use /configview &lt;VAR&gt; to view a specific variable.</i>"
    )
    await message.reply_text(text)
