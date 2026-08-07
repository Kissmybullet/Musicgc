import html

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Country"
__help__ = """
<b>Country Commands:</b>

• <code>/country [name]</code> — Get info about a country
"""


@Client.on_message(filters=Filter.command("country"))
async def country_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text(
            "Usage: <code>/country [name]</code>\nExample: <code>/country India</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"country_cmd error: {reply.message}")
        return

    name = parts[1].strip()
    msg = await message.reply_text(f"🌍 Searching for <b>{html.escape(name)}</b>...")
    if isinstance(msg, types.Error):
        return

    try:
        from countryinfo import CountryInfo

        country = CountryInfo(name)
        info = country.info()

        native = info.get("nativeName", "N/A")
        capital = info.get("capital", "N/A")
        if isinstance(capital, list):
            capital = ", ".join(capital)

        currencies = info.get("currencies", [])
        if isinstance(currencies, list):
            currencies = ", ".join(currencies) if currencies else "N/A"

        languages = info.get("languages", [])
        if isinstance(languages, list):
            languages = ", ".join(languages) if languages else "N/A"

        region = info.get("region", "N/A")
        subregion = info.get("subregion", "N/A")
        population = info.get("population", "N/A")
        if isinstance(population, int):
            population = f"{population:,}"

        area = info.get("area", "N/A")
        if isinstance(area, (int, float)):
            area = f"{area:,.0f} km²"

        calling_codes = info.get("callingCodes", [])
        if isinstance(calling_codes, list):
            calling_codes = (
                ", ".join(f"+{c}" for c in calling_codes) if calling_codes else "N/A"
            )

        tld = info.get("tld", [])
        if isinstance(tld, list):
            tld = " ".join(tld) if tld else "N/A"

        borders = info.get("borders", [])
        if isinstance(borders, list):
            borders = ", ".join(borders) if borders else "None"

        result = (
            f"🌍 <b>{html.escape(info.get('name', name))}</b>\n\n"
            f"<b>Native Name:</b> <code>{html.escape(str(native))}</code>\n"
            f"<b>Capital:</b> <code>{html.escape(str(capital))}</code>\n"
            f"<b>Region:</b> <code>{html.escape(str(region))}</code>\n"
            f"<b>Subregion:</b> <code>{html.escape(str(subregion))}</code>\n"
            f"<b>Population:</b> <code>{html.escape(str(population))}</code>\n"
            f"<b>Area:</b> <code>{html.escape(str(area))}</code>\n"
            f"<b>Currencies:</b> <code>{html.escape(str(currencies))}</code>\n"
            f"<b>Languages:</b> <code>{html.escape(str(languages))}</code>\n"
            f"<b>Calling Codes:</b> <code>{html.escape(str(calling_codes))}</code>\n"
            f"<b>TLD:</b> <code>{html.escape(str(tld))}</code>\n"
            f"<b>Borders:</b> <code>{html.escape(str(borders))}</code>"
        )

        await msg.edit_text(result)

    except ImportError:
        await msg.edit_text(
            "❌ The <code>countryinfo</code> package is not installed.\nInstall with: <code>pip install countryinfo</code>"
        )
    except Exception as e:
        await msg.edit_text(
            f"❌ Country not found or error: <code>{html.escape(str(e))}</code>"
        )
