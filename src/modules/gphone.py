import html

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Phone"
__help__ = """
<b>Phone Commands:</b>

• <code>/phone [number]</code> — Get info about a phone number
"""


@Client.on_message(filters=Filter.command("phone"))
async def phone_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text(
            "Usage: <code>/phone [+countrycode number]</code>\n"
            "Example: <code>/phone +1 202 555 0143</code>"
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"phone_cmd error: {reply.message}")
        return

    number = parts[1].strip()
    msg = await message.reply_text("📞 Checking phone number...")
    if isinstance(msg, types.Error):
        return

    try:
        import phonenumbers

        parsed = phonenumbers.parse(number, None)
        is_valid = phonenumbers.is_valid_number(parsed)
        is_possible = phonenumbers.is_possible_number(parsed)
        number_type = phonenumbers.number_type(parsed)

        type_map = {
            phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
            phonenumbers.PhoneNumberType.MOBILE: "Mobile",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
            phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
            phonenumbers.PhoneNumberType.VOIP: "VoIP",
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
            phonenumbers.PhoneNumberType.PAGER: "Pager",
            phonenumbers.PhoneNumberType.UAN: "UAN",
            phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
            phonenumbers.PhoneNumberType.UNKNOWN: "Unknown",
        }

        region = phonenumbers.region_code_for_number(parsed)
        country = (
            phonenumbers.region_code_to_country_name(region) if region else "Unknown"
        )

        formatted_intl = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        formatted_national = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.NATIONAL
        )
        formatted_e164 = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164
        )

        result = (
            f"📞 <b>Phone Number Info</b>\n\n"
            f"<b>Number:</b> <code>{html.escape(formatted_intl)}</code>\n"
            f"<b>National:</b> <code>{html.escape(formatted_national)}</code>\n"
            f"<b>E.164:</b> <code>{html.escape(formatted_e164)}</code>\n"
            f"<b>Valid:</b> {'✅' if is_valid else '❌'}\n"
            f"<b>Possible:</b> {'✅' if is_possible else '❌'}\n"
            f"<b>Type:</b> <code>{type_map.get(number_type, 'Unknown')}</code>\n"
            f"<b>Country:</b> <code>{html.escape(country)}</code>"
        )

        await msg.edit_text(result)

    except ImportError:
        await msg.edit_text(
            "❌ The <code>phonenumbers</code> package is not installed.\nInstall with: <code>pip install phonenumbers</code>"
        )
    except Exception as e:
        await msg.edit_text(f"❌ Error: <code>{html.escape(str(e))}</code>")
