#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import os
from pytdbot import Client, types
from src.core import Filter
from src.core._youtube import YouTubeData, YouTubeUtils

__mod_name__ = "Song"
__help__ = """
*✿ Song ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /song <query> ➛ Download songs.
"""

@Client.on_message(filters=Filter.command(["song"]))
async def gsong_cmd(c: Client, message: types.Message):
    """Download songs."""
    query = message.text.split(None, 1)
    if len(query) < 2:
        return await message.reply_text("Please give a song name or link to download.")
    
    msg = await message.reply_text("🔍 Searching...")
    if isinstance(msg, types.Error):
        return
        
    yt = YouTubeData(query[1])
    search_res = await yt.search()
    if isinstance(search_res, types.Error) or not search_res.results:
        return await msg.edit_text("❌ No results found.")
        
    track = search_res.results[0]
    await msg.edit_text(f"⏳ Downloading: **{track.title}**")
    
    try:
        track_info = await yt.get_track()
        if isinstance(track_info, types.Error):
            track_info = await YouTubeUtils.create_track_info({"id": track.id})
            
        file_path = await yt.download_track(track_info, video=False)
        if isinstance(file_path, types.Error) or not file_path:
            return await msg.edit_text("❌ Failed to download.")
            
        await msg.edit_text("📤 Uploading...")
        
        caption = f"🎧 **{track.title}**\n\nUploaded by {c.me.first_name}"
        
        await c.sendAudio(
            chat_id=message.chat_id,
            audio=types.InputFileLocal(path=str(file_path)),
            caption=caption,
            reply_to_message_id=message.id
        )
        
        await msg.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")
