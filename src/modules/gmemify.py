import os
import textwrap
import asyncio

from pytdbot import Client, types
from pytdbot.types import Message
from PIL import Image, ImageDraw, ImageFont

from src.core import Filter

__mod_name__ = "Mᴍғ"
__help__ = """ 
⫸ /mmf <ᴛᴇxᴛ> ◉ ᴛᴏ ᴍᴇᴍɪғʏ """


async def drawText(image_path, text):
    img = Image.open(image_path)

    i_width, i_height = img.size

    font_path = "src/modules/utils/font.ttf"
    if not os.path.exists(font_path):
        font_path = None

    if font_path:
        m_font = ImageFont.truetype(font_path, int((100 / 640) * i_width))
    else:
        m_font = ImageFont.load_default()

    if ";" in text:
        upper_text, lower_text = text.split(";", 1)
    else:
        upper_text = text
        lower_text = ""

    draw = ImageDraw.Draw(img)
    pad = 10

    def draw_text_with_outline(x, y, txt, font, draw_obj):
        draw_obj.text((x - 2, y - 2), txt, font=font, fill=(0, 0, 0))
        draw_obj.text((x + 2, y - 2), txt, font=font, fill=(0, 0, 0))
        draw_obj.text((x - 2, y + 2), txt, font=font, fill=(0, 0, 0))
        draw_obj.text((x + 2, y + 2), txt, font=font, fill=(0, 0, 0))
        draw_obj.text((x, y), txt, font=font, fill=(255, 255, 255))

    if not lower_text:
        wrapped_text = textwrap.wrap(upper_text, width=15)
        line_heights = []
        for line in wrapped_text:
            left, top, right, bottom = m_font.getbbox(line)
            line_heights.append(bottom - top)
            
        total_height = sum(line_heights) + pad * (max(len(line_heights) - 1, 0))
        current_y = (i_height - total_height) / 2
        
        for i, line in enumerate(wrapped_text):
            left, top, right, bottom = m_font.getbbox(line)
            u_width = right - left
            draw_text_with_outline(
                (i_width - u_width) / 2,
                current_y,
                line,
                m_font,
                draw,
            )
            current_y += line_heights[i] + pad
    else:
        current_h = 10
        if upper_text:
            for u_text in textwrap.wrap(upper_text, width=15):
                left, top, right, bottom = m_font.getbbox(u_text)
                u_width, u_height = right - left, bottom - top
                draw_text_with_outline(
                    ((i_width - u_width) / 2),
                    current_h,
                    u_text,
                    m_font,
                    draw,
                )
                current_h += u_height + pad

        if lower_text:
            wrapped_lower = textwrap.wrap(lower_text, width=15)
            lower_heights = [m_font.getbbox(l)[3] - m_font.getbbox(l)[1] for l in wrapped_lower]
            total_lower_height = sum(lower_heights) + pad * (max(len(lower_heights) - 1, 0))
            
            current_h = i_height - total_lower_height - 20
            for i, l_text in enumerate(wrapped_lower):
                left, top, right, bottom = m_font.getbbox(l_text)
                u_width = right - left
                draw_text_with_outline(
                    ((i_width - u_width) / 2),
                    current_h,
                    l_text,
                    m_font,
                    draw,
                )
                current_h += lower_heights[i] + pad

    image_name = "memify.webp"
    img.save(image_name, "webp")
    return image_name


@Client.on_message(filters=Filter.command(["mmf"]))
async def gmemify_cmd(c: Client, message: Message):
    """Add text to images."""
    chat_id = message.chat_id
    args = message.text.split(maxsplit=1)

    if not message.reply_to_message_id:
        return await message.reply_text(
            "Provide Some Text To Draw and reply to an image/sticker!"
        )

    replied = await message.getRepliedMessage()
    if isinstance(replied, types.Error):
        return await message.reply_text("Failed to get replied message.")

    if len(args) < 2:
        return await message.reply_text("You might want to try `/mmf text`")

    text = args[1].strip()

    content = replied.content
    file_id = None

    if isinstance(content, types.MessagePhoto):
        file_id = content.photo.sizes[-1].photo.id
    elif isinstance(content, types.MessageSticker):
        file_id = content.sticker.sticker.id
    elif isinstance(content, types.MessageDocument):
        file_id = content.document.document.id
    else:
        return await message.reply_text("```Reply to a image/sticker.```")

    msg = await message.reply_text("```Memifying this image! ✊🏻 ```")
    if isinstance(msg, types.Error):
        return

    downloaded = await c.downloadFile(
        file_id=file_id, priority=1, offset=0, limit=0, synchronous=True
    )
    if isinstance(downloaded, types.Error):
        return await c.editTextMessage(
            chat_id=chat_id, message_id=msg.id, text="Failed to download media."
        )

    path = getattr(downloaded, "local", None)
    if path:
        path = path.path
    else:
        path = getattr(downloaded, "path", None)

    if not path or not os.path.exists(path):
        await asyncio.sleep(2)
        if not path or not os.path.exists(path):
            return await c.editTextMessage(
                chat_id=chat_id,
                message_id=msg.id,
                text="File is still downloading, please try again.",
            )

    if path.endswith((".webm", ".tgs", ".mp4")):
        return await c.editTextMessage(
            chat_id=chat_id,
            message_id=msg.id,
            text="Animated stickers and videos are not supported for memify. Please reply to a static image or sticker.",
        )

    try:
        meme_path = await drawText(path, text)

        await c.sendPhoto(
            chat_id=chat_id,
            photo=types.InputFileLocal(path=meme_path),
            caption="Here is your meme!",
            reply_to_message_id=message.id,
        )

        await c.deleteMessages(chat_id=chat_id, message_ids=[msg.id], revoke=True)
        if os.path.exists(meme_path):
            os.remove(meme_path)
    except Exception as e:
        await c.editTextMessage(
            chat_id=chat_id,
            message_id=msg.id,
            text=f"Error generating meme: {str(e)}",
        )
