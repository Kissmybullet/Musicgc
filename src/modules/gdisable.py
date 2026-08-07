#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter, db, admins_only

__mod_name__ = "Disable"
__help__ = """
*✿ Dɪsᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /disable <cmd> ➛ Disables a command in the chat.
❍ /enable <cmd> ➛ Enables a disabled command.
❍ /disabled ➛ Lists all disabled commands in the chat.
"""

# Hardcoded commands that cannot be disabled
DISABLE_EXCEPTIONS = ["enable", "disable", "disabled", "start", "help", "admin", "admins"]


@Client.on_message(filters=Filter.command(["disable"]))
@admins_only(permissions="can_change_info")
async def disable_cmd(c: Client, message: Message):
    """Disables a command."""
    chat_id = message.chat_id
    if chat_id > 0:
        return await message.reply_text("This command can only be used in groups.")
        
    args = message.text.split()
    if len(args) < 2:
        return await message.reply_text("Please specify a command to disable.")
        
    cmd = args[1].lower().strip("/")
    if cmd in DISABLE_EXCEPTIONS:
        return await message.reply_text(f"You cannot disable `{cmd}`.")
        
    is_disabled = await db.group.is_command_disabled(chat_id, cmd)
    if is_disabled:
        return await message.reply_text(f"`{cmd}` is already disabled in this chat.")
        
    await db.group.disable_command(chat_id, cmd)
    await message.reply_text(f"Successfully disabled `{cmd}` in this chat.", parse_mode="markdown")


@Client.on_message(filters=Filter.command(["enable"]))
@admins_only(permissions="can_change_info")
async def enable_cmd(c: Client, message: Message):
    """Enables a command."""
    chat_id = message.chat_id
    if chat_id > 0:
        return await message.reply_text("This command can only be used in groups.")
        
    args = message.text.split()
    if len(args) < 2:
        return await message.reply_text("Please specify a command to enable.")
        
    cmd = args[1].lower().strip("/")
    is_disabled = await db.group.is_command_disabled(chat_id, cmd)
    
    if not is_disabled:
        return await message.reply_text(f"`{cmd}` is not disabled.")
        
    await db.group.enable_command(chat_id, cmd)
    await message.reply_text(f"Successfully enabled `{cmd}` in this chat.", parse_mode="markdown")


@Client.on_message(filters=Filter.command(["disabled"]))
async def disabled_cmd(c: Client, message: Message):
    """Lists disabled commands."""
    chat_id = message.chat_id
    if chat_id > 0:
        return await message.reply_text("This command can only be used in groups.")
        
    commands = await db.group.get_disabled_commands(chat_id)
    if not commands:
        return await message.reply_text("No commands are disabled in this chat.")
        
    text = "**Disabled Commands:**\n\n"
    for cmd in commands:
        text += f"❍ `{cmd}`\n"
        
    await message.reply_text(text, parse_mode="markdown")
