#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import random

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Truth or Dare"
__help__ = """
<b>Truth or Dare Commands:</b>

• <code>/truth</code> — Get a random truth question
• <code>/dare</code> — Get a random dare challenge
"""

TRUTHS = [
    "What is your most embarrassing moment?",
    "What is the last lie you told?",
    "What is the most childish thing you still do?",
    "What is a secret you have never told anyone?",
    "What is the craziest thing you have done for love?",
    "What is your biggest regret?",
    "What is the weirdest search in your browser history?",
    "What is the most embarrassing thing in your room?",
    "Have you ever pretended to like a gift? What was it?",
    "What is the worst date you have been on?",
    "What is something you are glad your family doesn't know about you?",
    "What is the most trouble you have been in?",
    "What is a habit you have that you know annoys people?",
    "What is the dumbest thing you have ever done?",
    "What is the most embarrassing thing you have posted online?",
    "What is the scariest thing that has ever happened to you?",
    "What is the meanest thing you have ever said to someone?",
    "If you could be invisible for a day, what would you do?",
    "What is the weirdest dream you have ever had?",
    "What is the worst gift you have ever received?",
    "Have you ever cheated on a test? How?",
    "What is the biggest secret you have kept from your best friend?",
    "What is the most embarrassing thing your parents have caught you doing?",
    "If you could switch lives with someone for a day, who would it be?",
    "What is something you have done that you think no one knows about?",
]

DARES = [
    "Do your best impression of a celebrity.",
    "Send a voice message singing your favorite song.",
    "Post a funny selfie on your profile.",
    "Do 20 push-ups right now.",
    "Speak in an accent for the next 5 messages.",
    "Call a friend and sing them a song.",
    "Dance for 30 seconds and record it.",
    "Eat a spoonful of something spicy.",
    "Text your crush something funny.",
    "Do a silly dance and send a video.",
    "Post the last photo in your camera roll.",
    "Change your profile picture to a funny photo for 1 hour.",
    "Do your best animal impression.",
    "Tell a joke to the group.",
    "Write a love letter to the person on your left.",
    "Do a handstand (or attempt one) and take a photo.",
    "Speak only in questions for the next 10 minutes.",
    "Send a voice message saying the alphabet backwards.",
    "Do 10 jumping jacks right now.",
    "Draw a self-portrait and share it.",
    "Pretend to be a waiter and take everyone's order.",
    "Do your best zombie impression.",
    "Send a message using only emojis.",
    "Imitate a teacher from your school.",
    "Do a dramatic reading of the last text you received.",
]


@Client.on_message(filters=Filter.command("truth"))
async def truth_cmd(c: Client, message: types.Message) -> None:
    question = random.choice(TRUTHS)
    reply = await message.reply_text(f"🔮 <b>Truth:</b>\n\n<i>{question}</i>")
    if isinstance(reply, types.Error):
        c.logger.warning(f"truth_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("dare"))
async def dare_cmd(c: Client, message: types.Message) -> None:
    dare = random.choice(DARES)
    reply = await message.reply_text(f"🔥 <b>Dare:</b>\n\n<i>{dare}</i>")
    if isinstance(reply, types.Error):
        c.logger.warning(f"dare_cmd error: {reply.message}")
