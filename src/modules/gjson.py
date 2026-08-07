import html

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "JSON"
__help__ = """
<b>JSON Commands:</b>

• <code>/json</code> — Show message as JSON (reply to a message)
"""


@Client.on_message(filters=Filter.command("json"))
async def json_cmd(c: Client, message: types.Message) -> None:
    if not message.reply_to_message_id:
        reply = await message.reply_text(
            "Reply to a message with <code>/json</code> to see its JSON data."
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"json_cmd error: {reply.message}")
        return

    replied = await message.getRepliedMessage()
    if isinstance(replied, types.Error):
        reply = await message.reply_text("Failed to get the replied message.")
        if isinstance(reply, types.Error):
            c.logger.warning(f"json_cmd error: {reply.message}")
        return

    try:
        import json as json_mod

        msg_dict = {
            "message_id": getattr(replied, "id", None),
            "sender_id": getattr(replied, "sender_id", None),
            "chat_id": getattr(replied, "chat_id", None),
            "date": getattr(replied, "date", None),
            "reply_to_message_id": getattr(replied, "reply_to_message_id", None),
            "forward_origin": str(getattr(replied, "forward_origin", None)),
        }

        if hasattr(replied, "content"):
            content = replied.content
            if hasattr(content, "text"):
                msg_dict["text"] = (
                    content.text.text
                    if hasattr(content.text, "text")
                    else str(content.text)
                )
            if hasattr(content, "caption"):
                msg_dict["caption"] = (
                    content.caption.text
                    if hasattr(content.caption, "text")
                    else str(content.caption)
                )
            content_type = type(content).__name__
            msg_dict["content_type"] = content_type

        json_str = json_mod.dumps(msg_dict, indent=2, default=str)

        if len(json_str) > 3500:
            json_str = json_str[:3500] + "\n... (truncated)"

        output = f"<pre>{html.escape(json_str)}</pre>"

        reply = await message.reply_text(output)
        if isinstance(reply, types.Error):
            c.logger.warning(f"json_cmd error: {reply.message}")

    except Exception as e:
        reply = await message.reply_text(f"Error: <code>{html.escape(str(e))}</code>")
        if isinstance(reply, types.Error):
            c.logger.warning(f"json_cmd error: {reply.message}")
