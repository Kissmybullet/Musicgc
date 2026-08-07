import os
import random

from pytdbot import Client, types

from src.core import Filter, group_db
from src.core._admins import is_admin

__mod_name__ = "Welcome Hidden"
__help__ = """
<b>Hidden Welcome Commands:</b>
/hiddenwelcome on/off - Enable or disable hidden welcome with generated image.
/welcomehidden on/off - Alias for hiddenwelcome.

When enabled, new members get a generated welcome card image
with chat and user profile photos merged into a background.
"""

IMG_LIST = [
    "https://graph.org//file/097531769fdd405480e59.jpg",
    "https://graph.org//file/fb12eda9238d49f937eff.jpg",
    "https://graph.org//file/3722679374ed1b56c03e2.jpg",
    "https://graph.org//file/725b0376a8b2f96bc3237.jpg",
    "https://graph.org//file/483972408aa4822b37bfa.jpg",
    "https://graph.org//file/74a85d290f10da5b8e2de.jpg",
]

FALLBACK_USER_PHOTO = "https://te.legra.ph/file/f72a978a5c26bf59fadf8.jpg"


def _create_circular_crop(img_path: str, size: int = 300) -> str:
    """Crop an image into a circle and save it."""
    from PIL import Image, ImageDraw

    img = Image.open(img_path)
    img.thumbnail((size, size))
    temp_path = "temp_thumb.jpg"
    img.save(temp_path)

    thumb = Image.open(temp_path)
    h, w = thumb.size
    lum_img = Image.new("L", thumb.size, 0)
    draw = ImageDraw.Draw(lum_img)
    draw.pieslice([(0, 0), (h, w)], 0, 360, fill=255, outline="white")

    import numpy as np

    img_arr = np.array(thumb)
    lum_arr = np.array(lum_img)
    final_arr = np.dstack((img_arr, lum_arr))
    result = Image.fromarray(final_arr)

    out_path = "circ_thumb.png"
    result.save(out_path)
    os.remove(temp_path)
    return out_path


def _generate_welcome_card(
    chat_photo_path: str,
    user_photo_path: str,
    background_url: str,
    chat_title: str,
    user_name: str,
    user_id: int,
) -> str:
    """Generate a welcome card image and return the output path."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

    try:
        font_path = "MelodyForgeBot/resources/default.ttf"
        if not os.path.exists(font_path):
            font_path = None

        chat_circle = _create_circular_crop(chat_photo_path)
        user_circle = _create_circular_crop(user_photo_path)

        bg = Image.open(
            background_url if background_url.startswith("http") else FALLBACK_USER_PHOTO
        )
        bg = bg.filter(ImageFilter.BoxBlur(8))
        combine = bg.copy()
        combine.paste(Image.open(chat_circle), (80, 132), mask=Image.open(chat_circle))
        combine.paste(Image.open(user_circle), (870, 132), mask=Image.open(user_circle))
        combine.save("merged.png")

        img = Image.open("merged.png")
        d = ImageDraw.Draw(img)

        if font_path:
            title_font = ImageFont.truetype(font_path, size=60)
            info_font = ImageFont.truetype(font_path, size=40)
        else:
            title_font = ImageFont.load_default()
            info_font = ImageFont.load_default()

        d.line((300, 570, 1000, 570), fill="white", width=4)
        d.arc((72, 130, 380, 435), start=0, end=360, fill="#0b0d0c", width=8)
        d.arc((862, 130, 1170, 435), start=0, end=360, fill="black", width=8)

        title_text = f"welcome to {chat_title}"
        d.text(
            (300, 50),
            title_text,
            font=title_font,
            fill=(224, 224, 224),
            stroke_width=2,
            stroke_fill="#f50727",
        )

        info_text = f" Name  :  {user_name}\n\nUser id  : {user_id}"
        d.multiline_text(
            (500, 580),
            info_text,
            font=info_font,
            fill=(224, 224, 224),
            stroke_width=2,
            stroke_fill="#f50727",
        )

        output = "final_welcome.jpg"
        img.crop((0, 0, 1280, 720)).save(output)

        for f in ["merged.png", "circ_thumb.png", "circ_thumb_1.png"]:
            if os.path.exists(f):
                os.remove(f)

        return output
    except Exception as e:
        print(f"Welcome card generation error: {e}")
        return ""


def mention_str(user) -> str:
    uid = getattr(user, "id", 0)
    name = getattr(user, "first_name", None) or "User"
    return f'<a href="tg://user?id={uid}">{name}</a>'


@Client.on_message(filters=Filter.command(["hiddenwelcome", "welcomehidden"]))
async def toggle_hidden_welcome(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        return await message.reply_text("This command only works in groups.")

    if not await is_admin(c, chat_id, user_id):
        return await message.reply_text("You need to be an admin to do this.")

    args = message.text.split()
    if len(args) < 2:
        data = await group_db.get_welcome(chat_id) or {}
        enabled = data.get("hidden_welcome", False)
        return await message.reply_text(
            f"<b>Hidden welcome is currently {'enabled' if enabled else 'disabled'}.</b>\n"
            f"Use /hiddenwelcome on/off to change."
        )

    setting = args[1].lower()
    if setting in ("on", "yes", "enable"):
        await group_db.set_welcome(chat_id, {"hidden_welcome": True})
        await message.reply_text("Hidden welcome with image generation enabled!")
    elif setting in ("off", "no", "disable"):
        await group_db.set_welcome(chat_id, {"hidden_welcome": False})
        await message.reply_text("Hidden welcome with image generation disabled!")
    else:
        await message.reply_text("Use /hiddenwelcome on or /hiddenwelcome off.")


@Client.on_updateNewMessage(filters=Filter.regex(r".*"))
async def hidden_welcome_watcher(c: Client, update: types.UpdateNewMessage):
    message = update.message
    if not message:
        return

    chat_id = message.chat_id
    if chat_id > 0:
        return

    content = message.content
    if not isinstance(content, types.MessageChatAddMembers):
        return

    data = await group_db.get_welcome(chat_id) or {}
    if not data.get("hidden_welcome", False):
        return

    for new_member_id in content.member_user_ids:
        user_result = await c.getUser(user_id=new_member_id)
        if isinstance(user_result, types.Error):
            continue

        user = user_result
        if (
            getattr(user, "type", None)
            and hasattr(user.type, "is_bot")
            and user.type.is_bot
        ):
            continue

        chat_info = await c.getChat(chat_id=chat_id)
        chat_title = (
            chat_info.title if not isinstance(chat_info, types.Error) else "this chat"
        )

        fullname = (getattr(user, "first_name", "") or "") + (
            " " + (getattr(user, "last_name", "") or "")
            if getattr(user, "last_name", None)
            else ""
        )
        fullname = fullname.strip() or "User"
        username = f"@{user.username}" if getattr(user, "username", None) else None

        try:
            bg_url = random.choice(IMG_LIST)

            user_photo = None
            if hasattr(user, "photo") and user.photo:
                photo_result = await c.downloadFile(file_id=user.photo.big_file_id)
                if not isinstance(photo_result, types.Error):
                    user_photo = photo_result.path

            chat_photo = None
            chat_info_full = await c.getChat(chat_id=chat_id)
            if (
                not isinstance(chat_info_full, types.Error)
                and hasattr(chat_info_full, "photo")
                and chat_info_full.photo
            ):
                photo_result = await c.downloadFile(
                    file_id=chat_info_full.photo.big_file_id
                )
                if not isinstance(photo_result, types.Error):
                    chat_photo = photo_result.path

            if user_photo and chat_photo:
                card_path = _generate_welcome_card(
                    chat_photo, user_photo, bg_url, chat_title, fullname, user.id
                )
                if card_path and os.path.exists(card_path):
                    caption = (
                        f"<b><u>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {chat_title}</u></b>\n"
                        f"ɴᴀᴍᴇ : {fullname[:45]}\n"
                        f"ᴜꜱᴇʀ ɪᴅ : <code>{user.id}</code>\n"
                        f"ᴜꜱᴇʀɴᴀᴍᴇ : <code>{username or 'N/A'}</code>\n"
                        f"ᴍᴇɴᴛɪᴏɴ : {mention_str(user)}"
                    )
                    from src.core._config import config

                    markup = types.ReplyMarkupInlineKeyboard(
                        rows=[
                            [
                                types.InlineKeyboardButton(
                                    text="➕ ᴀᴅᴅ ᴍᴇ ➕",
                                    type=types.InlineKeyboardButtonTypeUrl(
                                        url=f"https://t.me/{c.me.username}?startgroup=true"
                                    ),
                                )
                            ]
                        ]
                    )
                    await c.sendPhoto(
                        chat_id=chat_id,
                        photo=types.InputFileLocal(path=card_path),
                        caption=caption,
                        parse_mode="html",
                        reply_markup=markup,
                    )
                    os.remove(card_path)
                    continue
        except Exception as e:
            print(f"Hidden welcome error: {e}")

        mention = mention_str(user)
        text = (
            f"<b><u>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {chat_title}</u></b>\n"
            f"ɴᴀᴍᴇ : {fullname[:45]}\n"
            f"ᴜꜱᴇʀ ɪᴅ : <code>{user.id}</code>\n"
            f"ᴜꜱᴇʀɴᴀᴍᴇ : <code>{username or 'N/A'}</code>\n"
            f"ᴍᴇɴᴛɪᴏɴ : {mention}"
        )
        from src.core._config import config

        markup = types.ReplyMarkupInlineKeyboard(
            rows=[
                [
                    types.InlineKeyboardButton(
                        text="➕ ᴀᴅᴅ ᴍᴇ ➕",
                        type=types.InlineKeyboardButtonTypeUrl(
                            url=f"https://t.me/{c.me.username}?startgroup=true"
                        ),
                    )
                ]
            ]
        )
        await c.sendTextMessage(
            chat_id=chat_id,
            text=text,
            parse_mode="html",
            reply_markup=markup,
        )
