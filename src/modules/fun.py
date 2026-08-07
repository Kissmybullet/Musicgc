#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import random

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Fun"
__help__ = """
<b>Fun Commands:</b>

• <code>/runs</code> — Run away!
• <code>/slap [user]</code> — Slap someone
• <code>/pat [user]</code> — Pat someone
• <code>/roll</code> — Roll a dice (1-100)
• <code>/toss</code> — Flip a coin
• <code>/shrug</code> — Shrug
• <code>/bluetext</code> — Blue text
• <code>/rlg</code> — Rock, Lizard, Spock
• <code>/decide</code> — Make a decision
• <code>/8ball [question]</code> — Ask the magic 8-ball
• <code>/table</code> — Flip a table
• <code>/shout [text]</code> — SHOUT TEXT
"""

RUNS_TEXT = [
    "*runs away*",
    "*runs away screaming*",
    "*disappears in a puff of smoke*",
    "*flees into the shadows*",
    "*vanishes dramatically*",
    "*nopes out of here*",
    "*teleports away*",
    "*sprints away*",
    "*yeets itself into the void*",
    "*backs away slowly*",
]

SLAP_TEMPLATES = [
    "{user1} slaps {user2} with a giant fish! 🐟",
    "{user1} slaps {user2} with a rubber chicken! 🐔",
    "{user1} slaps {user2} with a baguette! 🥖",
    "{user1} slaps {user2} with a flip-flop! 🩴",
    "{user1} slaps {user2} with a wet noodle! 🍝",
    "{user1} slaps {user2} with a pillow! 🛏️",
    "{user1} gives {user2} a firm slap! ✋",
    "{user1} slaps {user2} with a newspaper! 📰",
    "{user1} slaps {user2} with a pool noodle! 🏊",
    "{user1} slaps {user2} with a book of knowledge! 📚",
]

PAT_TEMPLATES = [
    "{user1} pats {user2} on the head gently! 🥰",
    "{user1} gives {user2} a warm pat! ❤️",
    "{user1} pats {user2} lovingly! 🤗",
    "{user1} gives {user2} a reassuring pat! 😊",
    "{user1} pats {user2} on the back! 👍",
    "{user1} gently pets {user2}! ✨",
    "{user1} gives {user2} a head pat! 💕",
    "{user1} pats {user2} like a good boy/girl! 🐶",
]

BLUE_TEXTS = [
    "A̷̢͝M̵̛̛I̶̿ ̸̌̕T̷̊H̶̿I̶̿S̶̿ ̶̿B̶̿L̶̿U̶̿E̶̿?̶̿",
    "T̶̿H̶̿I̶̿S̶̿ ̶̿I̶̿S̶̿ ̶̿B̶̿L̶̿U̶̿E̶̿ ̶̿T̶̿E̶̿X̶̿T̶̿",
    "I̶̿ ̶̿A̶̿M̶̿ ̶̿B̶̿L̶̿U̶̿E̶̿",
    "b̵̛̈l̶̿u̶̿e̶̿ ̶̿t̶̿e̶̿x̶̿t̶̿ ̶̿a̶̿c̶̿t̶̿i̶̿v̶̿a̶̿t̶̿e̶̿d̶̿",
]

RLG_ITEMS = [
    "🎭 Rock",
    "📜 Paper",
    "✂️ Scissors",
    "🦎 Lizard",
    "🖖 Spock",
]

DECIDE_REPLIES = [
    "Yes! Definitely!",
    "Nope, not at all.",
    "Maybe... who knows?",
    "Absolutely!",
    "Not a chance.",
    "I'd say yes.",
    "I'd say no.",
    "Ask me again later.",
    "Go for it!",
    "Think again.",
    "Without a doubt!",
    "I wouldn't count on it.",
    "Sure, why not?",
    "Better not.",
    "The stars say yes.",
    "The stars say no.",
]

EIGHT_BALL_REPLIES = [
    "🔮 It is certain.",
    "🔮 It is decidedly so.",
    "🔮 Without a doubt.",
    "🔮 Yes, definitely.",
    "🔮 You may rely on it.",
    "🔮 As I see it, yes.",
    "🔮 Most likely.",
    "🔮 Outlook good.",
    "🔮 Yes.",
    "🔮 Signs point to yes.",
    "🔮 Reply hazy, try again.",
    "🔮 Ask again later.",
    "🔮 Better not tell you now.",
    "🔮 Cannot predict now.",
    "🔮 Concentrate and ask again.",
    "🔮 Don't count on it.",
    "🔮 My reply is no.",
    "🔮 My sources say no.",
    "🔮 Outlook not so good.",
    "🔮 Very doubtful.",
]

SHOUT_REPLACE = {
    "a": "A",
    "b": "B",
    "c": "C",
    "d": "D",
    "e": "E",
    "f": "F",
    "g": "G",
    "h": "H",
    "i": "I",
    "j": "J",
    "k": "K",
    "l": "L",
    "m": "M",
    "n": "N",
    "o": "O",
    "p": "P",
    "q": "Q",
    "r": "R",
    "s": "S",
    "t": "T",
    "u": "U",
    "v": "V",
    "w": "W",
    "x": "X",
    "y": "Y",
    "z": "Z",
    " ": " ",
}


def _get_text_args(message: types.Message) -> str:
    text = message.text or ""
    parts = text.split(None, 1)
    return parts[1] if len(parts) > 1 else ""


@Client.on_message(filters=Filter.command("runs"))
async def runs_cmd(c: Client, message: types.Message) -> None:
    reply = await message.reply_text(random.choice(RUNS_TEXT))
    if isinstance(reply, types.Error):
        c.logger.warning(f"runs_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("slap"))
async def slap_cmd(c: Client, message: types.Message) -> None:
    args = _get_text_args(message)
    user = await message.mention()
    if args:
        target = args
    elif message.reply_to_message_id:
        replied = await message.getRepliedMessage()
        if isinstance(replied, types.Error):
            target = "themselves"
        elif replied.sender_id and isinstance(
            replied.sender_id, types.MessageSenderUser
        ):
            target_user = await c.getUser(user_id=replied.sender_id.user_id)
            target = (
                target_user.first_name
                if not isinstance(target_user, types.Error)
                else str(replied.sender_id.user_id)
            )
        else:
            target = "themselves"
    else:
        target = "themselves"
    text = random.choice(SLAP_TEMPLATES).format(user1=user, user2=target)
    reply = await message.reply_text(text)
    if isinstance(reply, types.Error):
        c.logger.warning(f"slap_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("pat"))
async def pat_cmd(c: Client, message: types.Message) -> None:
    args = _get_text_args(message)
    user = await message.mention()
    if args:
        target = args
    elif message.reply_to_message_id:
        replied = await message.getRepliedMessage()
        if isinstance(replied, types.Error):
            target = "themselves"
        elif replied.sender_id and isinstance(
            replied.sender_id, types.MessageSenderUser
        ):
            target_user = await c.getUser(user_id=replied.sender_id.user_id)
            target = (
                target_user.first_name
                if not isinstance(target_user, types.Error)
                else str(replied.sender_id.user_id)
            )
        else:
            target = "themselves"
    else:
        target = "themselves"
    text = random.choice(PAT_TEMPLATES).format(user1=user, user2=target)
    reply = await message.reply_text(text)
    if isinstance(reply, types.Error):
        c.logger.warning(f"pat_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("roll"))
async def roll_cmd(c: Client, message: types.Message) -> None:
    result = random.randint(1, 100)
    reply = await message.reply_text(f"🎲 You rolled: <b>{result}</b>")
    if isinstance(reply, types.Error):
        c.logger.warning(f"roll_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("toss"))
async def toss_cmd(c: Client, message: types.Message) -> None:
    result = random.choice(["🪙 Heads!", "🪙 Tails!"])
    reply = await message.reply_text(result)
    if isinstance(reply, types.Error):
        c.logger.warning(f"toss_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("shrug"))
async def shrug_cmd(c: Client, message: types.Message) -> None:
    reply = await message.reply_text(r"¯\_(ツ)_/¯")
    if isinstance(reply, types.Error):
        c.logger.warning(f"shrug_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("bluetext"))
async def bluetext_cmd(c: Client, message: types.Message) -> None:
    reply = await message.reply_text(random.choice(BLUE_TEXTS))
    if isinstance(reply, types.Error):
        c.logger.warning(f"bluetext_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("rlg"))
async def rlg_cmd(c: Client, message: types.Message) -> None:
    picks = random.sample(RLG_ITEMS, 3)
    text = "🎭 " + " vs ".join(picks)
    reply = await message.reply_text(text)
    if isinstance(reply, types.Error):
        c.logger.warning(f"rlg_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("decide"))
async def decide_cmd(c: Client, message: types.Message) -> None:
    reply = await message.reply_text(random.choice(DECIDE_REPLIES))
    if isinstance(reply, types.Error):
        c.logger.warning(f"decide_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("8ball"))
async def eightball_cmd(c: Client, message: types.Message) -> None:
    args = _get_text_args(message)
    if not args:
        reply = await message.reply_text(
            "❓ Ask me a question! Usage: <code>/8ball [question]</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"eightball_cmd error: {reply.message}")
        return
    reply = await message.reply_text(random.choice(EIGHT_BALL_REPLIES))
    if isinstance(reply, types.Error):
        c.logger.warning(f"eightball_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("table"))
async def table_cmd(c: Client, message: types.Message) -> None:
    table_art = (
        "(╯°□°)╯︵ ┻━┻\n\n┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻\n\n┬─┬ノ( º _ ºノ)\n\n( ͡° ͜ʖ ͡°)ﾉ⌐■-■"
    )
    reply = await message.reply_text(table_art)
    if isinstance(reply, types.Error):
        c.logger.warning(f"table_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("shout"))
async def shout_cmd(c: Client, message: types.Message) -> None:
    args = _get_text_args(message)
    if not args:
        reply = await message.reply_text(
            "📝 What do you want to shout? Usage: <code>/shout [text]</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"shout_cmd error: {reply.message}")
        return
    shouted = ""
    for char in args:
        if char in SHOUT_REPLACE:
            shouted += SHOUT_REPLACE[char]
        else:
            shouted += char
    spaced = " ".join(list(shouted))
    reply = await message.reply_text(spaced)
    if isinstance(reply, types.Error):
        c.logger.warning(f"shout_cmd error: {reply.message}")
