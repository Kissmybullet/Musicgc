#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import base64
import html

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Encode/Decode"
__help__ = """
<b>Encoding Commands:</b>

• <code>/encode [text]</code> — Base64 encode text
• <code>/decode [text]</code> — Base64 decode text
• <code>/morseencode [text]</code> — Encode text to Morse code
• <code>/morsedecode [text]</code> — Decode Morse code to text
"""

MORSE_CODE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    "!": "-.-.--",
    "/": "-..-.",
    "(": "-.--.",
    ")": "-.--.-",
    "&": ".-...",
    ":": "---...",
    ";": "-.-.-.",
    "=": "-...-",
    "+": ".-.-.",
    "-": "-....-",
    "_": "..--.-",
    '"': ".-..-.",
    "'": ".----.",
    "@": ".--.-.",
}

MORSE_DECODE = {v: k for k, v in MORSE_CODE.items()}


def _get_args(message: types.Message) -> str:
    text = message.text or ""
    parts = text.split(None, 1)
    return parts[1] if len(parts) > 1 else ""


@Client.on_message(filters=Filter.command("encode"))
async def encode_cmd(c: Client, message: types.Message) -> None:
    args = _get_args(message)
    if not args:
        reply = await message.reply_text(
            "ℹ️ Please provide text to encode.\nUsage: <code>/encode [text]</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"encode_cmd error: {reply.message}")
        return

    try:
        encoded = base64.b64encode(args.encode()).decode()
        reply = await message.reply_text(
            f"<b>🔐 Base64 Encoded:</b>\n<code>{html.escape(encoded)}</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"encode_cmd error: {reply.message}")
    except Exception as e:
        reply = await message.reply_text(
            f"❌ Error: <code>{html.escape(str(e))}</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"encode_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("decode"))
async def decode_cmd(c: Client, message: types.Message) -> None:
    args = _get_args(message)
    if not args:
        reply = await message.reply_text(
            "ℹ️ Please provide text to decode.\nUsage: <code>/decode [text]</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"decode_cmd error: {reply.message}")
        return

    try:
        decoded = base64.b64decode(args.encode()).decode()
        reply = await message.reply_text(
            f"<b>🔓 Base64 Decoded:</b>\n<code>{html.escape(decoded)}</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"decode_cmd error: {reply.message}")
    except Exception as e:
        reply = await message.reply_text(
            f"❌ Error: <code>{html.escape(str(e))}</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"decode_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("morseencode"))
async def morse_encode_cmd(c: Client, message: types.Message) -> None:
    args = _get_args(message)
    if not args:
        reply = await message.reply_text(
            "ℹ️ Please provide text to encode.\nUsage: <code>/morseencode [text]</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"morse_encode_cmd error: {reply.message}")
        return

    morse = []
    for char in args.upper():
        if char == " ":
            morse.append("/")
        elif char in MORSE_CODE:
            morse.append(MORSE_CODE[char])
        else:
            morse.append(char)

    result = " ".join(morse)
    reply = await message.reply_text(
        f"<b>📡 Morse Encoded:</b>\n<code>{html.escape(result)}</code>"
    )
    if isinstance(reply, types.Error):
        c.logger.warning(f"morse_encode_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("morsedecode"))
async def morse_decode_cmd(c: Client, message: types.Message) -> None:
    args = _get_args(message)
    if not args:
        reply = await message.reply_text(
            "ℹ️ Please provide Morse code to decode.\nUsage: <code>/morsedecode [morse]</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"morse_decode_cmd error: {reply.message}")
        return

    decoded = []
    for word in args.split(" / "):
        chars = []
        for code in word.split():
            if code in MORSE_DECODE:
                chars.append(MORSE_DECODE[code])
            else:
                chars.append(code)
        decoded.append("".join(chars))

    result = " ".join(decoded)
    reply = await message.reply_text(
        f"<b>📡 Morse Decoded:</b>\n<code>{html.escape(result)}</code>"
    )
    if isinstance(reply, types.Error):
        c.logger.warning(f"morse_decode_cmd error: {reply.message}")
