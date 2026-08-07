import html

from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "Speedtest"
__help__ = """
<b>Speedtest Commands:</b>

• <code>/speedtest</code> — Run an internet speed test
"""


def _format_speed(bps: float) -> str:
    if bps >= 1_000_000:
        return f"{bps / 1_000_000:.2f} Mbps"
    if bps >= 1_000:
        return f"{bps / 1_000:.2f} Kbps"
    return f"{bps:.0f} bps"


@Client.on_message(filters=Filter.command("speedtest"))
async def speedtest_cmd(c: Client, message: types.Message) -> None:
    msg = await message.reply_text("🏓 Running speed test...")
    if isinstance(msg, types.Error):
        return

    try:
        import speedtest

        s = speedtest.Speedtest()
        await msg.edit_text("🏓 Getting best server...")
        s.get_best_server()

        await msg.edit_text("🏓 Testing download speed...")
        download = s.download()

        await msg.edit_text("🏓 Testing upload speed...")
        upload = s.upload()

        results = s.results.dict()
        server = results.get("server", {})
        server_name = server.get("name", "Unknown")
        server_country = server.get("country", "Unknown")
        ping = results.get("ping", 0)

        result_text = (
            f"🏓 <b>Speed Test Results</b>\n\n"
            f"<b>Download:</b> <code>{_format_speed(download)}</code>\n"
            f"<b>Upload:</b> <code>{_format_speed(upload)}</code>\n"
            f"<b>Ping:</b> <code>{ping:.2f} ms</code>\n"
            f"<b>Server:</b> <code>{html.escape(server_name)}, {html.escape(server_country)}</code>"
        )

        await msg.edit_text(result_text)

    except ImportError:
        await msg.edit_text(
            "❌ The <code>speedtest-cli</code> package is not installed."
        )
    except Exception as e:
        await msg.edit_text(f"❌ Speed test failed: <code>{html.escape(str(e))}</code>")
