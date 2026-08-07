#  Copyright (c) 2026 TheMukeshDev
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the MelodyForgeBot project. All rights reserved where applicable.

import importlib
import math
import os
import pkgutil

from pytdbot import Client, types

from src import __version__
from src.core import (
    Filter,
    SupportButton,
    config,
)
from src.core import db
from src.core.buttons import CLOSE_BTN, CHANNEL_BTN, GROUP_BTN

# ─────────────────────────────────────────────
# Auto-discover all modules with __mod_name__ and __help__
# ─────────────────────────────────────────────

HELP_MODULES: dict[str, str] = {}  # {mod_name: help_text}


def _load_module_help() -> None:
    """Scan all modules in this package for __mod_name__ and __help__."""
    global HELP_MODULES
    modules_dir = os.path.dirname(os.path.abspath(__file__))

    for _, module_name, _ in pkgutil.iter_modules([modules_dir]):
        if module_name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"src.modules.{module_name}")
            mod_name = getattr(mod, "__mod_name__", None)
            mod_help = getattr(mod, "__help__", None)
            if mod_name and mod_help:
                HELP_MODULES[mod_name] = mod_help
        except Exception:
            continue

    # Sort alphabetically for consistent ordering
    HELP_MODULES = dict(sorted(HELP_MODULES.items(), key=lambda x: x[0].lower()))


# Load on import
_load_module_help()

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

MODULES_PER_PAGE = 12  # 12 buttons per page (3 rows of 4)

START_TEXT = """
**•──────────────────────•**
**❍ ʜᴇʏ {},**
**•──────────────────────•**
**❍ ɪ ᴀᴍ {},**
**❍ ɪ ʜᴀᴠᴇ sᴘᴇᴄɪᴀʟ ғᴇᴀᴛᴜʀᴇs**
**•──────────────────────•**
**❍ ᴜsᴇʀs ➛ {} **
**❍ ᴄʜᴀᴛs ➛ {} **
**•──────────────────────•**
**❍ ɪ ʜᴀᴠᴇ ᴍᴏsᴛ ᴘᴏᴡᴇʀғᴜʟʟ ғᴇᴀᴛᴜʀᴇs**
**ᴍᴜsɪᴄ ʙᴏᴛ + ᴄʜᴀᴛʙᴏᴛ + ᴍᴀɴᴀɢᴇᴍᴇɴᴛ**
**•──────────────────────•**
"""

HELP_HEADER = """
<b>◎ Hᴇʟᴘ Mᴇɴᴜ</b>

🛡 <b>Gʀᴏᴜᴘ Mᴀɴᴀɢᴇᴍᴇɴᴛ</b> | 🎵 <b>Mᴜꜱɪᴄ & Uᴛɪʟɪᴛɪᴇꜱ</b>

<b>{total}</b> ᴍᴏᴅᴜʟᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ. Tᴀᴘ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʜᴇʟᴘ ꜰᴏʀ ᴛʜᴀᴛ ᴍᴏᴅᴜʟᴇ.

<i>Pᴀɢᴇ {page}/{total_pages}</i>
"""


# ─────────────────────────────────────────────
# Button Builders
# ─────────────────────────────────────────────


def _get_total_pages() -> int:
    """Get total number of help pages."""
    return max(1, math.ceil(len(HELP_MODULES) / MODULES_PER_PAGE))


def _build_help_page_markup(page: int) -> types.ReplyMarkupInlineKeyboard:
    """Build a Rose-style paginated help menu for a given page.

    Layout: 3 rows of 2 module buttons + navigation row + close/home row.
    """
    module_names = list(HELP_MODULES.keys())
    total_pages = _get_total_pages()

    start_idx = page * MODULES_PER_PAGE
    end_idx = min(start_idx + MODULES_PER_PAGE, len(module_names))
    page_modules = module_names[start_idx:end_idx]

    rows = []

    # Module buttons: 4 per row (3 rows of 4)
    for i in range(0, len(page_modules), 4):
        row = []
        for mod_name in page_modules[i : i + 4]:
            row.append(
                types.InlineKeyboardButton(
                    text=mod_name,
                    type=types.InlineKeyboardButtonTypeCallback(
                        data=f"hmod_{mod_name}".encode()
                    ),
                )
            )
        rows.append(row)

    # Navigation row: ◀️ Page X/Y ▶️
    # Navigation row: ◀️ Home ▶️
    if total_pages > 1:
        prev_page = (page - 1) % total_pages
        next_page = (page + 1) % total_pages
        nav_row = [
            types.InlineKeyboardButton(
                text="←",
                type=types.InlineKeyboardButtonTypeCallback(
                    data=f"hpage_{prev_page}".encode()
                ),
            ),
            types.InlineKeyboardButton(
                text="🏠 Hᴏᴍᴇ",
                type=types.InlineKeyboardButtonTypeCallback(data=b"help_back"),
            ),
            types.InlineKeyboardButton(
                text="→",
                type=types.InlineKeyboardButtonTypeCallback(
                    data=f"hpage_{next_page}".encode()
                ),
            ),
        ]
        rows.append(nav_row)
    else:
        # If only 1 page, just show Home
        rows.append(
            [
                types.InlineKeyboardButton(
                    text="🏠 Hᴏᴍᴇ",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"help_back"),
                ),
            ]
        )

    return types.ReplyMarkupInlineKeyboard(rows=rows)


def _build_module_help_markup(mod_name: str) -> types.ReplyMarkupInlineKeyboard:
    """Build the back button markup shown when viewing a specific module's help."""
    module_names = list(HELP_MODULES.keys())

    # Find which page this module is on
    try:
        idx = module_names.index(mod_name)
        page = idx // MODULES_PER_PAGE
    except ValueError:
        page = 0

    rows = []

    # Back to help list + Home
    rows.append(
        [
            types.InlineKeyboardButton(
                text="← Bᴀᴄᴋ",
                type=types.InlineKeyboardButtonTypeCallback(
                    data=f"hpage_{page}".encode()
                ),
            ),
            types.InlineKeyboardButton(
                text="🏠 Hᴏᴍᴇ",
                type=types.InlineKeyboardButtonTypeCallback(data=b"help_back"),
            ),
        ]
    )

    return types.ReplyMarkupInlineKeyboard(rows=rows)


def add_me_markup(username: str) -> types.ReplyMarkupInlineKeyboard:
    """Creates the inline keyboard for the bot's start message."""
    return types.ReplyMarkupInlineKeyboard(
        rows=[
            [
                types.InlineKeyboardButton(
                    text="• ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ •",
                    type=types.InlineKeyboardButtonTypeUrl(
                        url=f"https://t.me/{username}?startgroup=true"
                    ),
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="• ᴜᴘᴅᴀᴛᴇ •",
                    type=types.InlineKeyboardButtonTypeUrl(
                        url="https://t.me/Flame_Bots"
                    ),
                ),
                types.InlineKeyboardButton(
                    text="• ꜱᴜᴘᴘᴏʀᴛ •",
                    type=types.InlineKeyboardButtonTypeUrl(url=config.SUPPORT_GROUP),
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="• ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs •",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"Main_help"),
                ),
            ],
        ]
    )


def _build_main_help_markup() -> types.ReplyMarkupInlineKeyboard:
    """Builds the main help menu markup."""
    return types.ReplyMarkupInlineKeyboard(
        rows=[
            [
                types.InlineKeyboardButton(
                    text="• ᴍᴀɴᴀɢᴇ •",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"hpage_0"),
                ),
                types.InlineKeyboardButton(
                    text="• ᴍᴜsɪᴄ •",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"Music_"),
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="• ʜᴏᴍᴇ •",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"help_back"),
                ),
            ],
        ]
    )


# ─────────────────────────────────────────────
# /start Command
# ─────────────────────────────────────────────


@Client.on_message(filters=Filter.command(["start"]))
async def start_cmd(c: Client, message: types.Message) -> None:
    """Handles the /start command.

    In a group, it sends a welcome message. In a private chat, it sends
    the main start message with a menu.

    Args:
        c (Client): The pytdbot client instance.
        message (types.Message): The message object containing the command.
    """
    chat_id = message.chat_id
    bot_name = c.me.first_name
    mention = await message.mention()

    if chat_id < 0:  # Group
        alive_text = (
            f"❍ ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ...!\n\n❍ **ɪ ᴅɪᴅɴ'ᴛ sʟᴇᴘᴛ ʙᴀʙʏ.**\n\n❍ ᴜᴘᴛɪᴍᴇ ➛ `100%`"
        )
        reply = await message.reply_photo(
            photo=config.START_IMG,
            caption=alive_text,
            reply_markup=types.ReplyMarkupInlineKeyboard(
                rows=[
                    [
                        types.InlineKeyboardButton(
                            text="• ꜱᴜᴘᴘᴏʀᴛ •",
                            type=types.InlineKeyboardButtonTypeUrl(
                                url=config.SUPPORT_GROUP
                            ),
                        )
                    ]
                ]
            ),
            parse_mode="markdown",
        )
    else:  # Private chat
        user_id = message.from_id
        sender = await c.getUser(user_id=user_id) if user_id else None
        import pytdbot

        first_name = (
            sender.first_name
            if sender and not isinstance(sender, pytdbot.types.Error)
            else "User"
        )
        first_name = first_name.replace("*", "").replace("_", "").replace("`", "")
        bot_fn = bot_name.replace("*", "").replace("_", "").replace("`", "")
        mention_md = f"[{first_name}](tg://user?id={user_id})"

        num_users = len(await db.get_all_users())
        num_chats = len(await db.get_all_chats())
        reply = await message.reply(
    TEXT
        )
            caption=START_TEXT.format(mention_md, bot_fn, num_users, num_chats),
            reply_markup=add_me_markup(c.me.usernames.editable_username),
            parse_mode="markdown",
        )

    if isinstance(reply, types.Error):
        c.logger.warning(f"Failed to send start reply: {reply.message}")


# ─────────────────────────────────────────────
# /help Command
# ─────────────────────────────────────────────


@Client.on_message(filters=Filter.command(["help"]))
async def help_cmd(c: Client, message: types.Message) -> None:
    """Handles the /help command.

    Sends the first page of the paginated help menu with module buttons.
    """
    text = f"✦ ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ꜰᴏʀ {c.me.first_name}"
    markup = _build_main_help_markup()

    reply = await message.reply_photo(
        photo=config.START_IMG,
        caption=text,
        reply_markup=markup,
        parse_mode="html",
    )
    if isinstance(reply, types.Error):
        c.logger.warning(f"Failed to send help reply: {reply.message}")


# ─────────────────────────────────────────────
# Callback Handlers for Help Pages
# ─────────────────────────────────────────────

async def _edit_start_msg(message: types.UpdateNewCallbackQuery, text: str, markup, parse_mode="html"):
    msg = await message.getMessage()
    if msg and getattr(msg, "content", None) and type(msg.content).__name__ in ("MessagePhoto", "MessageVideo", "MessageAnimation"):
        return await message.edit_message_caption(caption=text, reply_markup=markup, parse_mode=parse_mode)
    return await message.edit_message_text(text, reply_markup=markup, parse_mode=parse_mode)


@Client.on_updateNewCallbackQuery(filters=Filter.regex(r"hpage_.*"))
async def callback_help_page(c: Client, message: types.UpdateNewCallbackQuery) -> None:
    """Handles pagination buttons (◀️ ▶️) for the help menu."""
    data = message.payload.data.decode()

    try:
        page = int(data.split("_", 1)[1])
    except (ValueError, IndexError):
        await message.answer("⚠️ Invalid page.")
        return None

    total = len(HELP_MODULES)
    total_pages = _get_total_pages()

    if page < 0 or page >= total_pages:
        page = 0

    text = HELP_HEADER.format(total=total, page=page + 1, total_pages=total_pages)
    markup = _build_help_page_markup(page)

    result = await _edit_start_msg(message, text, markup, "html")
    if isinstance(result, types.Error):
        c.logger.error(f"Edit failed: {result.message}")
    return None


@Client.on_updateNewCallbackQuery(filters=Filter.regex(r"hmod_.*"))
async def callback_help_module(
    c: Client, message: types.UpdateNewCallbackQuery
) -> None:
    """Handles module help button clicks — shows the module's help text."""
    data = message.payload.data.decode()
    mod_name = data.split("_", 1)[1] if "_" in data else ""

    if mod_name not in HELP_MODULES:
        await message.answer(f"⚠️ Module '{mod_name}' not found.")
        return None

    import html
    help_text = html.escape(HELP_MODULES[mod_name])
    text = f"<b>📦 {mod_name} Module</b>\n{help_text}"

    markup = _build_module_help_markup(mod_name)

    result = await _edit_start_msg(message, text, markup, "html")
    if isinstance(result, types.Error):
        c.logger.error(f"Edit failed: {result.message}")
    return None


@Client.on_updateNewCallbackQuery(filters=Filter.regex(r"help_back"))
async def callback_help_home(c: Client, message: types.UpdateNewCallbackQuery) -> None:
    """Handles the 🏠 Home button — returns to start message."""
    await message.answer("🏠 Returning to home...")

    user_id = message.sender_user_id
    if not user_id:
        return None

    user = await c.getUser(user_id=user_id)

    import pytdbot

    if isinstance(user, pytdbot.types.Error):
        return None

    first_name = user.first_name.replace("*", "").replace("_", "").replace("`", "")
    bot_fn = c.me.first_name.replace("*", "").replace("_", "").replace("`", "")
    mention_md = f"[{first_name}](tg://user?id={user_id})"

    text = START_TEXT.format(
        mention_md, bot_fn, len(await db.get_all_users()), len(await db.get_all_chats())
    )

    result = await _edit_start_msg(
        message,
        text,
        add_me_markup(c.me.usernames.editable_username),
        "markdown",
    )
    if isinstance(result, types.Error):
        c.logger.error(f"Edit failed: {result.message}")
    return None


@Client.on_updateNewCallbackQuery(filters=Filter.regex(r"Main_help"))
async def callback_main_help(c: Client, message: types.UpdateNewCallbackQuery) -> None:
    """Handles the Main Help button."""
    text = f"✦ ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ꜰᴏʀ {c.me.first_name}"
    markup = _build_main_help_markup()
    result = await _edit_start_msg(message, text, markup, "html")
    if isinstance(result, types.Error):
        c.logger.error(f"Edit failed: {result.message}")
    return None


@Client.on_updateNewCallbackQuery(filters=Filter.regex(r"Music_"))
async def callback_music_help(c: Client, message: types.UpdateNewCallbackQuery) -> None:
    """Handles the Music help sections."""
    data = message.payload.data.decode()

    markup = types.ReplyMarkupInlineKeyboard(
        rows=[
            [
                types.InlineKeyboardButton(
                    text="ᴀᴅᴍɪɴ",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"Music_admin"),
                ),
                types.InlineKeyboardButton(
                    text="ᴘʟᴀʏ",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"Music_play"),
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="ʙᴏᴛ",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"Music_bot"),
                ),
                
            ],
            [
                types.InlineKeyboardButton(
                    text="← ʙᴀᴄᴋ",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"Main_help"),
                ),
            ],
        ]
    )

    if data == "Music_":
        text = "✿ ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ꜰᴏʀ ᴍᴜꜱɪᴄ ✿"
    elif data == "Music_admin":
        text = "*✿ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*\n\n❅ ᴀᴅᴍɪɴs ᴀɴᴅ ᴀᴜᴛʜ ᴜsᴇʀᴀ ᴄᴏᴍᴍᴀɴᴅs ❅\n\n❍ /pause ➛ ᴩᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ.\n❍ /resume ➛ ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ.\n❍ /skip ➛ sᴋɪᴩ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛ sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ.\n❍ /end ᴏʀ /stop ➛ ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ᴇɴᴅ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ.\n❍ /player ➛ ɢᴇᴛ ᴀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴩʟᴀʏᴇʀ ᴩᴀɴᴇʟ.\n❍ /queue ➛ sʜᴏᴡs ᴛʜᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs ʟɪsᴛ."
        markup = types.ReplyMarkupInlineKeyboard(
            rows=[
                [
                    types.InlineKeyboardButton(
                        text="ʙᴀᴄᴋ",
                        type=types.InlineKeyboardButtonTypeCallback(data=b"Music_"),
                    )
                ]
            ]
        )
    elif data == "Music_play":
        text = "*✿ ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*\n\n❍ /play ➛ ʙᴏᴛ ᴡɪʟʟ ꜱᴛᴀʀᴛ ᴘʟᴀʏɪɴɢ ʏᴏᴜʀ ɢɪᴠᴇɴ ϙᴜᴇʀʏ on ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴏʀ ꜱᴛʀᴇᴀᴍ ʟɪᴠᴇ ʟɪɴᴋꜱ ᴏɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛꜱ.\n\n❍ /playforce ᴏʀ /vplayforce ᴏʀ /cplayforce ➛ ғᴏʀᴄᴇ ᴘʟᴀʏ ꜱᴛᴏᴘꜱ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀʏɪɴɢ ᴛʀᴀᴄᴋ ᴏɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀɴᴅ ꜱᴛᴀʀᴛꜱ ᴘʟᴀʏɪɴɢ ᴛʜᴇ ꜱᴇᴀʀᴄʜᴇᴅ ᴛʀᴀᴄᴋ ɪɴꜱᴛᴀɴᴛʟʏ ᴡɪᴛʜᴏᴜᴛ ᴅɪꜱᴛᴜʀʙɪɴɢ/clearing queue.\n\n❍ /channelplay ➛ [ᴄʜᴀᴛ ᴜꜱᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ] ᴏʀ [ᴅɪꜱᴀʙʟᴇ] - ᴄᴏɴɴᴇᴄᴛ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ꜱᴛʀᴇᴀᴍ ᴍᴜꜱɪᴄ ᴏɴ ᴄʜᴀɴɴᴇʟ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ғʀᴏᴍ ʏᴏᴜʀ ɢʀᴏᴜᴘ."
        markup = types.ReplyMarkupInlineKeyboard(
            rows=[
                [
                    types.InlineKeyboardButton(
                        text="ʙᴀᴄᴋ",
                        type=types.InlineKeyboardButtonTypeCallback(data=b"Music_"),
                    )
                ]
            ]
        )
    elif data == "Music_bot":
        text = "*✿ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*\n\n❍ /stats ➛ ɢᴇᴛ ᴛᴏᴘ 10 ᴛʀᴀᴄᴋꜱ ɢʟᴏʙᴀʟ ꜱᴛᴀᴛꜱ, ᴛᴏᴘ 10 ᴜꜱᴇʀꜱ ᴏғ ʙᴏᴛ, ᴛᴏᴘ 10 ᴄʜᴀᴛꜱ ᴏɴ ʙᴏᴛ, ᴛᴏᴘ 10 ᴘʟᴀʏᴇᴅ ɪɴ ᴀ ᴄʜᴀᴛ ᴇᴛᴄ ᴇᴛᴄ.\n\n❍ /sudolist ➛ ᴄʜᴇᴄᴋ sᴜᴅᴏ ᴜsᴇʀs ᴏғ ᴀʙɢ ʙᴏᴛ\n\n❍ /lyrics [ᴍᴜsɪᴄ ɴᴀᴍᴇ] ➛ sᴇᴀʀᴄʜᴇs ʟʏʀɪᴄs ғᴏʀ ᴛʜᴇ ᴘᴀʀᴛɪᴄᴜʟᴀʀ ᴍᴜsɪᴄ ᴏɴ ᴡᴇʙ.\n\n❍ /song [ᴛʀᴀᴄᴋ ɴᴀᴍᴇ] or [ʏᴛ ʟɪɴᴋ] ➛ ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴʏ ᴛʀᴀᴄᴋ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ɪɴ ᴍᴘ3 or ᴍᴘ4 ғᴏʀᴍᴀᴛꜱ.\n\n❍ /player ➛ ɢᴇt ᴀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴘʟᴀʏɪɴɢ ᴘᴀɴᴇʟ.\n\n❍ /queue ᴏʀ /cqueue ➛ ᴄʜᴇᴄᴋ Qᴜᴇᴜᴇ ʟɪꜱᴛ ᴏꜰ ᴍᴜꜱɪᴄ."
        markup = types.ReplyMarkupInlineKeyboard(
            rows=[
                [
                    types.InlineKeyboardButton(
                        text="ʙᴀᴄᴋ",
                        type=types.InlineKeyboardButtonTypeCallback(data=b"Music_"),
                    )
                ]
            ]
        )
    

    result = await _edit_start_msg(message, text, markup, "markdown")
    if isinstance(result, types.Error):
        c.logger.error(f"Edit failed: {result.message}")
    return None


@Client.on_updateNewCallbackQuery(filters=Filter.regex(r"Manage_"))
async def callback_manage_help(
    c: Client, message: types.UpdateNewCallbackQuery
) -> None:
    """Handles the Group Management help sections."""
    data = message.payload.data.decode()

    markup = types.ReplyMarkupInlineKeyboard(
        rows=[
            [
                types.InlineKeyboardButton(
                    text="Nᴏᴛᴇꜱ",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"Manage_notes"),
                ),
                types.InlineKeyboardButton(
                    text="Fɪʟᴛᴇʀꜱ",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"Manage_filters"),
                ),
                types.InlineKeyboardButton(
                    text="Fᴇᴅꜱ",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"Manage_feds"),
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="ʙᴀᴄᴋ",
                    type=types.InlineKeyboardButtonTypeCallback(data=b"Main_help"),
                ),
            ],
        ]
    )

    if data == "Manage_":
        text = "✿ ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ꜰᴏʀ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ✿\n\nSelect a sub-category below to view commands for Notes, Filters, or Feds."
    elif data == "Manage_notes":
        text = "*✿ Nᴏᴛᴇꜱ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*\n\n❍ /get <notename> ➛ Get a note.\n❍ /save <notename> <text> ➛ Save a new note.\n❍ /notes ➛ List all notes in the chat.\n❍ /clear <notename> ➛ Delete a note."
        markup = types.ReplyMarkupInlineKeyboard(
            rows=[
                [
                    types.InlineKeyboardButton(
                        text="ʙᴀᴄᴋ",
                        type=types.InlineKeyboardButtonTypeCallback(data=b"Manage_"),
                    )
                ]
            ]
        )
    elif data == "Manage_filters":
        text = "*✿ Fɪʟᴛᴇʀꜱ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*\n\n❍ /filter <keyword> <reply> ➛ Adds a filter to the chat.\n❍ /filters ➛ Lists all active filters.\n❍ /stop <keyword> ➛ Stops a filter."
        markup = types.ReplyMarkupInlineKeyboard(
            rows=[
                [
                    types.InlineKeyboardButton(
                        text="ʙᴀᴄᴋ",
                        type=types.InlineKeyboardButtonTypeCallback(data=b"Manage_"),
                    )
                ]
            ]
        )
    elif data == "Manage_feds":
        text = "*✿ Fᴇᴅꜱ ᴄᴏᴍᴍᴀɴᴅꜱ ✿*\n\n❍ /newfed <fedname> ➛ Create a new federation.\n❍ /joinfed <fedid> ➛ Join a federation.\n❍ /fban <user> ➛ Ban a user across all chats in the fed.\n❍ /fedinfo <fedid> ➛ Get info about a federation."
        markup = types.ReplyMarkupInlineKeyboard(
            rows=[
                [
                    types.InlineKeyboardButton(
                        text="ʙᴀᴄᴋ",
                        type=types.InlineKeyboardButtonTypeCallback(data=b"Manage_"),
                    )
                ]
            ]
        )

    result = await _edit_start_msg(message, text, markup, "markdown")
    if isinstance(result, types.Error):
        c.logger.error(f"Edit failed: {result.message}")
    return None
