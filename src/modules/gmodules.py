#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import os
from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter, admins_only

__mod_name__ = "Modules"
__help__ = """
*✿ Mᴏᴅᴜʟᴇꜱ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /modules ➛ Lists all actively loaded modules in the bot.
"""


@Client.on_message(filters=Filter.command(["modules", "plugins"]))
@admins_only(only_owner=True)
async def gmodules_cmd(c: Client, message: Message):
    """Lists all loaded modules."""
    module_dir = "src/modules"
    loaded_modules = []
    
    if os.path.exists(module_dir):
        for f in os.listdir(module_dir):
            if f.endswith(".py") and not f.startswith("_"):
                loaded_modules.append(f.replace(".py", ""))
                
    loaded_modules.sort()
    
    text = f"**📦 Loaded Modules ({len(loaded_modules)}):**\n\n"
    text += ", ".join([f"`{m}`" for m in loaded_modules])
    
    await message.reply_text(text, parse_mode="markdown")
