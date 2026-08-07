from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Animations"
__help__ = """
<b>Animation Commands:</b>

• <code>/love [user]</code> — Love animation
• <code>/hack [user]</code> — Hack animation
• <code>/kill [user]</code> — Kill animation
• <code>/bombs [user]</code> — Bomb animation
• <code>/police [user]</code> — Police animation
"""

LOVE_ANIM = [
    "❤️ Initializing love.exe...",
    "❤️💕 Scanning for love...",
    "❤️💕💖 Found love!",
    "❤️💕💖💘 LOVE OVERLOAD!",
    "❤️💕💖💘💗 You are loved! 💗💘💖💕❤️",
]

HACK_ANIM = [
    "💻 Initializing hack.exe...",
    "💻🔑 Finding vulnerabilities...",
    "💻🔑🔓 Breaching firewall...",
    "💻🔑🔓📡 Accessing mainframe...",
    "💻🔑🔓📡⚠️ HACK COMPLETE! You've been hacked!",
]

KILL_ANIM = [
    "💀 Initializing kill.exe...",
    "💀🔪 Locating target...",
    "💀🔪🎯 Target locked!",
    "💀🔪🎯☠️ Engaging target!",
    "💀🔪🎯☠️💀 TARGET ELIMINATED!",
]

BOMBS_ANIM = [
    "💣 Initializing bombs.exe...",
    "💣🧨 Arming explosives...",
    "💣🧨💥 Dropping bombs!",
    "💣🧨💥💥💥 BOMBARDMENT!",
    "💣🧨💥💥💥🤯 TOTAL DESTRUCTION!",
]

POLICE_ANIM = [
    "🚔 Initializing police.exe...",
    "🚔🚨 Scanning area...",
    "🚔🚨👮 Dispatching units!",
    "🚔🚨👮🚔🚨 YOU ARE SURROUNDED!",
    "🚔🚨👮🚔🚨🚔 POLICE WANTED LEVEL: MAX!",
]


def _get_text_args(message: types.Message) -> str:
    text = message.text or ""
    parts = text.split(None, 1)
    return parts[1] if len(parts) > 1 else ""


async def _animate(c: Client, message: types.Message, frames: list) -> None:
    target = ""
    args = _get_text_args(message)
    if args:
        target = f" for <b>{args}</b>"
    elif message.reply_to_message_id:
        target = " for the replied user"

    user = await message.mention()
    reply = await message.reply_text(f"{user} has initiated an action{target}!")
    if isinstance(reply, types.Error):
        c.logger.warning(f"animate error: {reply.message}")
        return

    for frame in frames:
        result = await reply.edit_text(frame)
        if isinstance(result, types.Error):
            c.logger.warning(f"animate frame error: {result.message}")
            break


@Client.on_message(filters=Filter.command("love"))
async def love_cmd(c: Client, message: types.Message) -> None:
    await _animate(c, message, LOVE_ANIM)


@Client.on_message(filters=Filter.command("hack"))
async def hack_cmd(c: Client, message: types.Message) -> None:
    await _animate(c, message, HACK_ANIM)


@Client.on_message(filters=Filter.command("kill"))
async def kill_cmd(c: Client, message: types.Message) -> None:
    await _animate(c, message, KILL_ANIM)


@Client.on_message(filters=Filter.command("bombs"))
async def bombs_cmd(c: Client, message: types.Message) -> None:
    await _animate(c, message, BOMBS_ANIM)


@Client.on_message(filters=Filter.command("police"))
async def police_cmd(c: Client, message: types.Message) -> None:
    await _animate(c, message, POLICE_ANIM)
