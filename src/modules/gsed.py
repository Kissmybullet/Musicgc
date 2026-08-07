#  Ported from LadyRezebb-reference/MukeshRobot/modules/sed.py
#  Regex substitution on replied-to messages

import re
import sre_constants

from pytdbot import Client, types

from src.core import Filter
from src.core._admins import check_permissions

__mod_name__ = "Sed"
__help__ = """
<b>Sed Commands:</b>
s/&lt;regex&gt;/&lt;replacement&gt;/[flags] - Apply regex substitution to replied message

Flags: g (global), i (case-insensitive)
Example: s/foo/bar/g
"""

DELIMITERS = ("/", ":", "|", "_")


def separate_sed(sed_string: str):
    """Parse a sed-like string into (pattern, replacement, flags)."""
    if (
        len(sed_string) >= 3
        and sed_string[1] in DELIMITERS
        and sed_string.count(sed_string[1]) >= 2
    ):
        delim = sed_string[1]
        start = counter = 2
        while counter < len(sed_string):
            if sed_string[counter] == "\\":
                counter += 1
            elif sed_string[counter] == delim:
                replace = sed_string[start:counter]
                counter += 1
                start = counter
                break
            counter += 1
        else:
            return None

        while counter < len(sed_string):
            if (
                sed_string[counter] == "\\"
                and counter + 1 < len(sed_string)
                and sed_string[counter + 1] == delim
            ):
                sed_string = sed_string[:counter] + sed_string[counter + 1 :]
            elif sed_string[counter] == delim:
                replace_with = sed_string[start:counter]
                counter += 1
                break
            counter += 1
        else:
            return replace, sed_string[start:], ""

        flags = ""
        if counter < len(sed_string):
            flags = sed_string[counter:]
        return replace, replace_with, flags.lower()


@Client.on_updateNewMessage(filters=Filter.regex(r"^s([/:|_]).*?\1.*"))
async def sed_handler(c: Client, update: types.UpdateNewMessage):
    message = update.message
    if not message:
        return

    chat_id = message.chat_id
    if chat_id > 0:
        return

    text = None
    if isinstance(message.content, types.MessageText):
        text = message.content.text.text

    if not text:
        return

    sed_result = separate_sed(text)
    if not sed_result:
        return

    if not message.reply_to_message_id:
        return

    replied = await message.getRepliedMessage()
    if isinstance(replied, types.Error):
        return

    to_fix = None
    if isinstance(replied.content, types.MessageText):
        to_fix = replied.content.text.text
    elif hasattr(replied.content, "caption"):
        to_fix = replied.content.caption

    if not to_fix:
        return

    repl, repl_with, flags = sed_result
    if not repl:
        await c.sendTextMessage(
            chat_id=chat_id,
            text="You're trying to replace... nothing with something?",
            reply_to_message_id=message.id,
        )
        return

    try:
        if "g" in flags and "i" in flags:
            text_result = re.sub(repl, repl_with, to_fix, flags=re.IGNORECASE)
        elif "i" in flags:
            text_result = re.sub(repl, repl_with, to_fix, count=1, flags=re.IGNORECASE)
        elif "g" in flags:
            text_result = re.sub(repl, repl_with, to_fix)
        else:
            text_result = re.sub(repl, repl_with, to_fix, count=1)
    except sre_constants.error:
        await c.sendTextMessage(
            chat_id=chat_id,
            text="Do you even sed? Apparently not.",
            reply_to_message_id=message.id,
        )
        return

    text_result = text_result.strip()
    if not text_result:
        return

    if len(text_result) > 4096:
        await c.sendTextMessage(
            chat_id=chat_id,
            text="The result of the sed command was too long for Telegram!",
            reply_to_message_id=message.id,
        )
        return

    await c.sendTextMessage(
        chat_id=chat_id,
        text=text_result,
        reply_to_message_id=replied.id,
    )
