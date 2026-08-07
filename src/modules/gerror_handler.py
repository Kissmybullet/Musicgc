#  Ported from LadyRezebb-reference/MukeshRobot/modules/error_handler.py
#  Global error handler - logs errors

import html
import traceback

from pytdbot import Client, types

from src.core import OWNER_ID, EVENT_LOGS
from src.logger import LOGGER

__mod_name__ = "ErrorHandler"
__help__ = ""


async def handle_errors(c: Client, update: types.Update, error: Exception):
    """Global error handler. Register this with pytdbot's error handling."""
    LOGGER.warning(f"Error handling update: {error}")
    LOGGER.debug(traceback.format_exc())

    if EVENT_LOGS:
        try:
            error_text = html.escape(str(error))
            text = (
                f"<b>An error occurred:</b>\n"
                f"<code>{error_text}</code>\n\n"
                f"<b>Update:</b> <code>{html.escape(str(update))[:1000]}</code>"
            )
            await c.sendTextMessage(
                chat_id=EVENT_LOGS,
                text=text,
                parse_mode="html",
            )
        except Exception as e:
            LOGGER.warning(f"Failed to log error to EVENT_LOGS: {e}")
