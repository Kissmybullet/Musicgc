import random

from pytdbot import Client, types
from src.core import Filter

__mod_name__ = "Sᴇᴍxʏ"
__help__ = """
➻ /horny - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ʜᴏʀɴʏᴇꜱꜱ
➻ /gay - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ɢᴜʏɴᴇꜱꜱ
➻ /lezbian - ᴄʜᴇᴄᴋ ᴜʀ ᴄᴜʀʀᴇɴᴛ ʟᴀᴢʙɪᴀɴ
➻ /boob - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ʙᴏᴏʙꜱ ꜱɪᴢᴇ
➻ /cock - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴄᴏᴄᴋ ꜱɪᴢᴇ
➻ /cute - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴄᴜᴛᴇɴᴇꜱꜱ
"""

HOT = "https://telegra.ph/file/daad931db960ea40c0fca.gif"
SMEXY = "https://telegra.ph/file/a23e9fd851fb6bc771686.gif"
LEZBIAN = "https://telegra.ph/file/5609b87f0bd461fc36acb.gif"
BIGBALL = "https://i.gifer.com/8ZUg.gif"
LANG = "https://telegra.ph/file/423414459345bf18310f5.gif"
CUTIE = "https://64.media.tumblr.com/d701f53eb5681e87a957a547980371d2/tumblr_nbjmdrQyje1qa94xto1_500.gif"

async def _send_rating(c: Client, message: types.Message, caption: str, gif_url: str):
    try:
        await c.sendAnimation(
            chat_id=message.chat_id,
            animation=types.InputFileRemote(id=gif_url),
            caption=caption,
            parse_mode="html",
            reply_to_message_id=message.id,
        )
    except Exception as e:
        c.logger.warning(f"Sexy module error: {e}")
        await message.reply_text(caption, parse_mode="html")

@Client.on_message(filters=Filter.command("horny"))
async def horny(c: Client, message: types.Message):
    mm = random.randint(1, 100)
    caption = f"<b>🔥</b> <a href='tg://user?id={message.sender_id}'>User</a> <b>ɪꜱ</b> {mm}<b>% ʜᴏʀɴʏ!</b>"
    await _send_rating(c, message, caption, HOT)

@Client.on_message(filters=Filter.command("gay"))
async def gay(c: Client, message: types.Message):
    mm = random.randint(1, 100)
    caption = f"<b>🍷</b> <a href='tg://user?id={message.sender_id}'>User</a> <b>ɪꜱ</b> {mm}<b>% ɢᴀʏ!</b>"
    await _send_rating(c, message, caption, SMEXY)

@Client.on_message(filters=Filter.command("lezbian"))
async def lezbian(c: Client, message: types.Message):
    mm = random.randint(1, 100)
    caption = f"<b>💜</b> <a href='tg://user?id={message.sender_id}'>User</a> <b>ɪꜱ</b> {mm}<b>% ʟᴇᴢʙɪᴀɴ!</b>"
    await _send_rating(c, message, caption, LEZBIAN)

@Client.on_message(filters=Filter.command("boob"))
async def boob(c: Client, message: types.Message):
    mm = random.randint(1, 100)
    caption = f"<b>🍒</b> <a href='tg://user?id={message.sender_id}'>User</a><b>'ꜱ ʙᴏᴏʙꜱ ꜱɪᴢᴇ ɪᴢ</b> {mm}<b>!</b>"
    await _send_rating(c, message, caption, BIGBALL)

@Client.on_message(filters=Filter.command("cock"))
async def cock(c: Client, message: types.Message):
    mm = random.randint(1, 100)
    caption = f"<b>🍆</b> <a href='tg://user?id={message.sender_id}'>User</a><b>'ꜱ ᴄᴏᴄᴋ ꜱɪᴢᴇ ɪᴢ</b> {mm}<b>ᴄᴍ</b>"
    await _send_rating(c, message, caption, LANG)

@Client.on_message(filters=Filter.command("cute"))
async def cute(c: Client, message: types.Message):
    mm = random.randint(1, 100)
    caption = f"<b>🍑</b> <a href='tg://user?id={message.sender_id}'>User</a> {mm}<b>% ᴄᴜᴛᴇ</b>"
    await _send_rating(c, message, caption, CUTIE)
