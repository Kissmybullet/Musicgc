import html

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Common"
__help__ = """
<b>Common Commands:</b>

• <code>/common [username]</code> — Show common groups with a user
"""


@Client.on_message(filters=Filter.command("common"))
async def common_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text("Usage: <code>/common [username]</code>")
        if isinstance(reply, types.Error):
            c.logger.warning(f"common_cmd error: {reply.message}")
        return

    username = parts[1].strip().lstrip("@")
    msg = await message.reply_text("🔍 Searching for user...")
    if isinstance(msg, types.Error):
        return

    try:
        result = await c.searchPublicChat(username=username)
        if isinstance(result, types.Error):
            await msg.edit_text(f"❌ Error: <code>{html.escape(result.message)}</code>")
            return

        user_id = result.id
        user_name = result.title or username

        my_chats = await c.getChats()
        if isinstance(my_chats, types.Error):
            await msg.edit_text("❌ Failed to fetch your chats.")
            return

        common = []
        for chat_id in my_chats.chat_ids[:200]:
            members = await c.getChatMembers(chat_id)
            if isinstance(members, types.Error):
                continue
            for member in members.members:
                if hasattr(member, "member_id") and hasattr(
                    member.member_id, "user_id"
                ):
                    if member.member_id.user_id == user_id:
                        chat_info = await c.getChat(chat_id)
                        if not isinstance(chat_info, types.Error):
                            common.append(chat_info.title or str(chat_id))
                        break

        if not common:
            await msg.edit_text(
                f"❌ No common groups found with <b>{html.escape(user_name)}</b>"
            )
            return

        text_out = f"👥 <b>Common groups with {html.escape(user_name)}:</b>\n\n"
        for i, name in enumerate(common[:20], 1):
            text_out += f"{i}. {html.escape(name)}\n"

        await msg.edit_text(text_out, disable_web_page_preview=True)

    except Exception as e:
        await msg.edit_text(f"❌ Error: <code>{html.escape(str(e))}</code>")
