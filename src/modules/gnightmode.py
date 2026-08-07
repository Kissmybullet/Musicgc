#  Ported from LadyRezebb-reference/MukeshRobot/modules/nightmode.py
#  Night mode: auto-mute/unmute groups at configured times

from datetime import datetime

from pytdbot import Client, types

from src.core import Filter, group_db
from src.core._admins import is_admin, load_admin_cache

__mod_name__ = "NightMode"
__help__ = """
<b>Night Mode Commands (admins only):</b>
/nightmode on &lt;start_time&gt; &lt;end_time&gt; - Enable night mode (e.g. /nightmode on 00:00 06:00)
/nightmode off - Disable night mode

Night mode automatically mutes all members during configured hours and unmutes them afterwards.
Times should be in HH:MM format (24h).
"""


def _parse_time(time_str: str) -> tuple[int, int] | None:
    """Parse HH:MM into (hour, minute) or None if invalid."""
    try:
        parts = time_str.strip().split(":")
        if len(parts) != 2:
            return None
        hour = int(parts[0])
        minute = int(parts[1])
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute
        return None
    except (ValueError, TypeError):
        return None


@Client.on_message(filters=Filter.command("nightmode"))
async def nightmode_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    load, _ = await load_admin_cache(c, chat_id)
    if not load:
        await message.reply_text("I need to be an admin to do this.")
        return

    args = message.text.split(None, 2)

    if len(args) < 2:
        existing = await group_db.get_nightmode(chat_id)
        if existing and existing.get("enabled"):
            start = existing.get("start_time", "??:??")
            end = existing.get("end_time", "??:??")
            await message.reply_text(
                f"Night mode is <b>enabled</b>.\n"
                f"Mute time: <code>{start}</code>\n"
                f"Unmute time: <code>{end}</code>"
            )
        else:
            await message.reply_text(
                "Night mode is <b>disabled</b>.\n"
                "Usage: /nightmode on &lt;start_time&gt; &lt;end_time&gt;\n"
                "Example: /nightmode on 00:00 06:00"
            )
        return

    subcmd = args[1].lower()

    if subcmd in ("off", "disable"):
        await group_db.rm_nightmode(chat_id)
        await message.reply_text("Night mode has been <b>disabled</b> for this chat.")
        return

    if subcmd in ("on", "enable"):
        if len(args) < 4:
            await message.reply_text(
                "Usage: /nightmode on &lt;start_time&gt; &lt;end_time&gt;\n"
                "Example: /nightmode on 00:00 06:00"
            )
            return

        start_parsed = _parse_time(args[2])
        end_parsed = _parse_time(args[3])

        if not start_parsed:
            await message.reply_text(
                f"Invalid start time: <code>{args[2]}</code>. Use HH:MM format."
            )
            return
        if not end_parsed:
            await message.reply_text(
                f"Invalid end time: <code>{args[3]}</code>. Use HH:MM format."
            )
            return

        start_time = f"{start_parsed[0]:02d}:{start_parsed[1]:02d}"
        end_time = f"{end_parsed[0]:02d}:{end_parsed[1]:02d}"

        await group_db.set_nightmode(
            chat_id,
            {
                "enabled": True,
                "start_time": start_time,
                "end_time": end_time,
            },
        )
        await message.reply_text(
            f"Night mode <b>enabled</b>!\n"
            f"Mute at: <code>{start_time}</code>\n"
            f"Unmute at: <code>{end_time}</code>"
        )
        return

    await message.reply_text(
        "Invalid subcommand. Use <code>/nightmode on</code> or <code>/nightmode off</code>."
    )
