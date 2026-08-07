#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import re
from pytdbot import Client
from pytdbot.types import Message
from src.core import Filter
from src.core import db
from src.core import admins_only

__mod_name__ = "Notes"
__help__ = """
*✿ Nᴏᴛᴇꜱ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*

❍ /get <notename> ➛ Get a note.
❍ /save <notename> <text/reply> ➛ Save a new note.
❍ /notes ➛ List all notes in the chat.
❍ /clear <notename> ➛ Delete a note.
❍ /clearall ➛ Delete all notes in the chat.
"""


@Client.on_message(filters=Filter.command(["save", "savenote"]))
@admins_only()
async def save_note(c: Client, message: Message):
    """Saves a note in the group."""
    chat_id = message.chat_id
    args = message.text.split(maxsplit=2)
    
    if len(args) < 2:
        return await message.reply_text("You need to specify a note name to save!")
        
    note_name = args[1].lower()
    
    if len(args) > 2:
        note_data = {"type": "text", "content": args[2]}
    elif message.reply_to_message_id:
        replied = await c.getMessage(chat_id, message.reply_to_message_id)
        if hasattr(replied, "text") and replied.text:
            note_data = {"type": "text", "content": replied.text}
        else:
            return await message.reply_text("I can only save text notes right now.")
    else:
        return await message.reply_text("You need to provide text or reply to a message to save a note!")
        
    await db.group.save_note(chat_id, note_name, note_data)
    await message.reply_text(f"Saved note `{note_name}`.")


@Client.on_message(filters=Filter.command(["get", "getnote"]))
async def get_note(c: Client, message: Message):
    """Gets a note in the group."""
    chat_id = message.chat_id
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await message.reply_text("You need to specify a note name to get!")
        
    note_name = args[1].lower()
    notes = await db.group.get_notes(chat_id)
    
    if note_name not in notes:
        return await message.reply_text(f"No note found for `{note_name}`.")
        
    note_data = notes[note_name]
    if note_data["type"] == "text":
        await message.reply_text(note_data["content"])


@Client.on_message(filters=Filter.command(["clear", "rmnote"]))
@admins_only()
async def clear_note(c: Client, message: Message):
    """Clears a note in the group."""
    chat_id = message.chat_id
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await message.reply_text("You need to specify a note name to clear!")
        
    note_name = args[1].lower()
    notes = await db.group.get_notes(chat_id)
    
    if note_name not in notes:
        return await message.reply_text(f"No note found for `{note_name}`.")
        
    await db.group.rm_note(chat_id, note_name)
    await message.reply_text(f"Cleared note `{note_name}`.")


@Client.on_message(filters=Filter.command(["notes", "saved"]))
async def list_notes(c: Client, message: Message):
    """Lists all notes in the group."""
    chat_id = message.chat_id
    notes = await db.group.get_notes(chat_id)
    
    if not notes:
        return await message.reply_text("There are no saved notes in this chat.")
        
    text = f"**Notes in this chat:**\n"
    for note_name in notes.keys():
        text += f" - `{note_name}`\n"
        
    text += "\nYou can get a note by using `/get notename`."
    await message.reply_text(text, parse_mode="markdown")


@Client.on_message(filters=Filter.command(["clearall"]))
@admins_only()
async def clear_all_notes(c: Client, message: Message):
    """Clears all notes in the group."""
    chat_id = message.chat_id
    await db.group.rm_all_notes(chat_id)
    await message.reply_text("Cleared all notes in this chat.")
