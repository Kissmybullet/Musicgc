#  Ported from LadyRezebb-reference/MukeshRobot/modules/reporting.py
#  Group management: Report settings

from pytdbot import Client, types

from src.core import Filter, group_db
from src.core._admins import is_admin

__mod_name__ = "Reports"
__help__ = """
/report &lt;reason&gt; - Reply to a message to report it to admins.
<b>Admins only:</b>
/reports &lt;on/off&gt; - Change report setting, or view current status.
"""


@Client.on_message(filters=Filter.command("reports"))
async def reports_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split(None, 1)

    if len(args) >= 2:
        val = args[1].strip().lower()
        if val in ("yes", "on"):
            await group_db.set_report_setting(chat_id, True)
            await message.reply_text(
                "Turned on reporting! Admins who have turned on reports will be notified when /report or @admin is called."
            )
            return
        elif val in ("no", "off"):
            await group_db.set_report_setting(chat_id, False)
            await message.reply_text(
                "Turned off reporting! No admins will be notified on /report or @admin."
            )
            return

    enabled = await group_db.get_report_setting(chat_id)
    status = "enabled" if enabled else "disabled"
    await message.reply_text(f"Reports are currently <b>{status}</b> in this group.")
