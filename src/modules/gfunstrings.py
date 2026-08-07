#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import random
from pytdbot import Client, types
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Fun Strings"
__help__ = """
*✿ Fᴜɴ Sᴛʀɪɴɢꜱ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /slap ➛ Slaps a user.
❍ /pat ➛ Pats a user.
❍ /hug ➛ Hugs a user.
"""

# Simple local lists for fun strings
SLAP_TEMPLATES = [
    "{user1} slaps {user2} around a bit with a large trout.",
    "{user1} gives {user2} a resounding slap across the face.",
    "{user1} slaps {user2} with a rubber chicken.",
    "{user1} smacks {user2} right on the forehead.",
]

PAT_TEMPLATES = [
    "{user1} gently pats {user2} on the head.",
    "{user1} gives {user2} a comforting pat on the back.",
    "{user1} softly pats {user2}.",
]

HUG_TEMPLATES = [
    "{user1} gives {user2} a warm, tight hug.",
    "{user1} wraps their arms around {user2} in a cozy hug.",
    "{user1} tackle-hugs {user2} to the ground!",
]

async def fun_action(c: Client, message: Message, templates: list):
    user1_name = "Someone"
    user = await c.getUser(user_id=message.from_id)
    if not isinstance(user, types.Error):
        user1_name = user.first_name
        
    user2_name = "themselves"
    if message.reply_to_message_id:
        replied = await c.getMessage(message.chat_id, message.reply_to_message_id)
        if replied and getattr(replied, "from_id", None):
            user2 = await c.getUser(user_id=replied.from_id)
            if not isinstance(user2, types.Error):
                user2_name = user2.first_name
                
    text = random.choice(templates).format(user1=f"**{user1_name}**", user2=f"**{user2_name}**")
    await message.reply_text(text, parse_mode="markdown")


@Client.on_message(filters=Filter.command(["slap"]))
async def slap_cmd(c: Client, message: Message):
    await fun_action(c, message, SLAP_TEMPLATES)


@Client.on_message(filters=Filter.command(["pat"]))
async def pat_cmd(c: Client, message: Message):
    await fun_action(c, message, PAT_TEMPLATES)


@Client.on_message(filters=Filter.command(["hug"]))
async def hug_cmd(c: Client, message: Message):
    await fun_action(c, message, HUG_TEMPLATES)
