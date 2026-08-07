#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import os
from datetime import datetime
from telegraph import Telegraph, exceptions, upload_file
from pytdbot import Client, types
from pytdbot.types import Message
from src.core import Filter

__mod_name__ = "T-Gʀᴀᴘʜ"
__help__ = """
ɪ ᴄᴀɴ ᴜᴘʟᴏᴀᴅ ғɪʟᴇs ᴛᴏ ᴛᴇʟᴇɢʀᴀᴘʜ
 ❍ /tgm :ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴏғ ʀᴇᴘʟɪᴇᴅ ᴍᴇᴅɪᴀ
 ❍ /tgt :ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴏғ ʀᴇᴘʟɪᴇᴅ ᴛᴇxᴛ
 ❍ /tgt [ᴄᴜsᴛᴏᴍ ɴᴀᴍᴇ]: ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴏғ ʀᴇᴘʟɪᴇᴅ ᴛᴇxᴛ ᴡɪᴛʜ ᴄᴜsᴛᴏᴍ ɴᴀᴍᴇ.
"""

telegraph = Telegraph(domain="graph.org")
try:
    r = telegraph.create_account(short_name="Controller")
except:
    pass

@Client.on_message(filters=Filter.command(["tgm", "tgt"]))
async def gtelegraph_cmd(c: Client, message: Message):
    if not message.reply_to_message_id:
        return await message.reply_text("Reply to a message to get a permanent telegra.ph link.")

    replied = await message.getRepliedMessage()
    if isinstance(replied, types.Error):
        return await message.reply_text("Could not fetch replied message.")

    cmd = message.text.split()[0].lower()
    start = datetime.now()
    
    if "tgm" in cmd:
        msg = await message.reply_text("Downloading media...")
        if isinstance(msg, types.Error):
            return
            
        file_id = None
        content = replied.content
        if isinstance(content, types.MessagePhoto):
            file_id = content.photo.sizes[-1].photo.id
        elif isinstance(content, types.MessageVideo):
            file_id = content.video.video.id
        elif isinstance(content, types.MessageAnimation):
            file_id = content.animation.animation.id
        elif isinstance(content, types.MessageDocument):
            file_id = content.document.document.id
            
        if not file_id:
            return await msg.edit_text("Reply to a photo or video.")
            
        downloaded = await c.downloadFile(file_id=file_id, priority=1, offset=0, limit=0, synchronous=True)
        if isinstance(downloaded, types.Error):
            return await msg.edit_text("Failed to download media.")
            
        path = getattr(downloaded, "local", None)
        path = path.path if path else getattr(downloaded, "path", None)
        
        if not path or not os.path.exists(path):
            import asyncio
            await asyncio.sleep(2)
            if not path or not os.path.exists(path):
                return await msg.edit_text("File download failed.")
                
        await msg.edit_text("Uploading to Telegraph...")
            
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                with open(path, "rb") as f:
                    resp = await client.post("https://graph.org/upload", files={"file": f}, timeout=60.0)
                if resp.status_code == 200:
                    res_json = resp.json()
                    if isinstance(res_json, list) and "src" in res_json[0]:
                        media_url = res_json[0]["src"]
                        end = datetime.now()
                        ms = (end - start).seconds
                        await msg.edit_text(
                            f"Uploaded to <a href='https://graph.org{media_url}'>Telegraph</a> in {ms} seconds.",
                            parse_mode="html"
                        )
                    else:
                        await msg.edit_text("ERROR: Failed to parse Telegraph response.")
                else:
                    await msg.edit_text(f"ERROR: {resp.status_code} - {resp.text}")
        except Exception as exc:
            await msg.edit_text("ERROR: " + str(exc))
        finally:
            if os.path.exists(path):
                os.remove(path)
            
    elif "tgt" in cmd:
        optional_title = ""
        args = message.text.split(None, 1)
        if len(args) > 1:
            optional_title = args[1]
            
        user_name = "User"
        if replied.sender_id and isinstance(replied.sender_id, types.MessageSenderUser):
            user_info = await c.getUser(replied.sender_id.user_id)
            if not isinstance(user_info, types.Error):
                user_name = user_info.first_name
                
        title_of_page = optional_title or user_name
        page_content = ""
        
        if hasattr(replied.content, "text"):
            page_content = replied.content.text.text
        elif hasattr(replied.content, "caption"):
            page_content = replied.content.caption.text
            
        if not page_content:
            return await message.reply_text("Reply to a text message.")
            
        page_content = page_content.replace("\n", "<br>")
        try:
            response = telegraph.create_page(title_of_page, html_content=page_content)
            end = datetime.now()
            ms = (end - start).seconds
            await message.reply_text(
                f"Pasted to <a href='https://graph.org/{response['path']}'>Telegraph</a> in {ms} seconds.",
                parse_mode="html"
            )
        except Exception as exc:
            await message.reply_text("ERROR: " + str(exc))
