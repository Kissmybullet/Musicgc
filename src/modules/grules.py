#  Ported from LadyRezebb-reference/MukeshRobot/modules/rules.py
#  Group management: View, Set, and Clear Rules

import html

from pytdbot import Client, types

from src.core import Filter, group_db
from src.core._admins import is_admin, load_admin_cache
from src.modules._helpers import get_chat_title, send_message

__mod_name__ = "Rules"
__help__ = """
<b>Rules Commands:</b>
/rules - Get the rules for this chat
/rules here - Get the rules and send them in chat
/setrules &lt;text&gt; - Set the rules for this chat (admin only)
/clearrules - Clear all rules (admin only)
"""


@Client.on_message(filters=Filter.command("rules"))
async def rules_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    args = message.text.split()

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    rules = await group_db.get_rules(chat_id)

    if not rules:
        await message.reply_text(
            "The group admins haven't set any rules for this chat yet. "
            "This probably doesn't mean it's lawless though...!"
        )
        return

    if len(args) >= 2 and args[1].lower() == "here":
        await message.reply_text(
            f"Rules for <b>{html.escape(await get_chat_title(c, message.chat_id))}</b>:\n\n{rules}"
        )
    else:
        bot_username = c.me.usernames.editable_username if c.me.usernames else "bot"
        await message.reply_text(
            "Click the button below to get the rules.",
            reply_markup=types.ReplyMarkupInlineKeyboard(
                rows=[
                    [
                        types.InlineKeyboardButton(
                            text="Rules",
                            type=types.InlineKeyboardButtonTypeUrl(
                                url=f"https://t.me/{bot_username}?start={chat_id}"
                            ),
                        )
                    ]
                ]
            ),
        )


@Client.on_message(filters=Filter.command("setrules"))
async def set_rules_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    args = message.text.split(None, 1)
    if len(args) < 2 or not args[1].strip():
        await message.reply_text("You didn't specify the rules text!")
        return

    rules_text = args[1].strip()
    await group_db.set_rules(chat_id, rules_text)
    await message.reply_text("Successfully set rules for this group.")


@Client.on_message(filters=Filter.command("clearrules"))
async def clear_rules_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    user_id = message.from_id

    if chat_id > 0:
        await message.reply_text("This command only works in groups.")
        return

    if not await is_admin(c, chat_id, user_id):
        await message.reply_text("You need to be an admin to do this.")
        return

    rules = await group_db.get_rules(chat_id)
    if not rules:
        await message.reply_text("There are no rules set in this chat.")
        return

    await group_db.clear_rules(chat_id)
    await message.reply_text("Successfully cleared rules!")
