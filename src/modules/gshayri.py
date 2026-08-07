#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import random
from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "Shayri"
__help__ = """
*✿ Sʜᴀʏʀɪ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /shayri ➛ Get a random Hindi Shayri.
"""

SHAYRIS = [
    "तेरी यादों से शुरू होती है मेरी हर सुबह,\nफिर कैसे कह दूँ कि मेरा दिन खराब है।",
    "मोहब्बत भी अजीब चीज है,\nजो जितना दर्द देता है, उससे उतना ही प्यार होता है।",
    "कुछ इस तरह से वो मुस्कुराते हैं,\nकि परेशान लोग भी उन्हें देखकर अपना गम भूल जाते हैं।",
    "हम तो तेरी आवाज़ से प्यार करते हैं,\nतसव्वुर में तेरे ही ख्यालों में खोए रहते हैं।",
    "दिल में दर्द है, आँखों में अश्क हैं,\nमगर लबों पर आज भी सिर्फ तेरा ही नाम है।",
]

@Client.on_message(filters=Filter.command(["shayri"]))
async def shayri_cmd(c: Client, message: Message):
    """Sends a random shayri."""
    text = random.choice(SHAYRIS)
    await message.reply_text(f"🌹 **{text}** 🌹", parse_mode="markdown")
