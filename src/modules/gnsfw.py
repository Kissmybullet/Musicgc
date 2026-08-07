import aiohttp
from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Anime Images"
__help__ = """
<b>Anime Image Commands:</b>

• <code>/neko</code> — Random neko image
• <code>/waifu</code> — Random waifu image
• <code>/hug</code> — Random hug image
• <code>/kiss</code> — Random kiss image
• <code>/slap</code> — Random slap image
• <code>/pat</code> — Random pat image
"""

NEKOS_URL = "https://nekos.life/api/v2/img/{endpoint}"

ENDPOINTS = {
    "neko": "neko",
    "waifu": "waifu",
    "hug": "hug",
    "kiss": "kiss",
    "slap": "slap",
    "pat": "pat",
}

LABELS = {
    "neko": "Neko",
    "waifu": "Waifu",
    "hug": "Hug",
    "kiss": "Kiss",
    "slap": "Slap",
    "pat": "Pat",
}


async def _get_image(endpoint: str) -> str | None:
    url = NEKOS_URL.format(endpoint=endpoint)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("url")
    except Exception:
        pass
    return None


async def _send_image(c: Client, message: types.Message, endpoint: str) -> None:
    label = LABELS.get(endpoint, endpoint.title())
    msg = await message.reply_text(f"Fetching {label}...")
    if isinstance(msg, types.Error):
        return

    url = await _get_image(endpoint)
    if not url:
        await msg.edit_text(f"Failed to fetch {label} image.")
        return

    await msg.delete()
    reply = await message.reply_photo(url, caption=f"Here's a {label}!")
    if isinstance(reply, types.Error):
        c.logger.warning(f"{endpoint}_cmd error: {reply.message}")


@Client.on_message(filters=Filter.command("neko"))
async def neko_cmd(c: Client, message: types.Message) -> None:
    await _send_image(c, message, "neko")


@Client.on_message(filters=Filter.command("waifu"))
async def waifu_cmd(c: Client, message: types.Message) -> None:
    await _send_image(c, message, "waifu")


@Client.on_message(filters=Filter.command("hug"))
async def hug_cmd(c: Client, message: types.Message) -> None:
    await _send_image(c, message, "hug")


@Client.on_message(filters=Filter.command("kiss"))
async def kiss_cmd(c: Client, message: types.Message) -> None:
    await _send_image(c, message, "kiss")


@Client.on_message(filters=Filter.command("slap"))
async def slap_image_cmd(c: Client, message: types.Message) -> None:
    await _send_image(c, message, "slap")


@Client.on_message(filters=Filter.command("pat"))
async def pat_image_cmd(c: Client, message: types.Message) -> None:
    await _send_image(c, message, "pat")
