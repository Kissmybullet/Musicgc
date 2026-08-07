import html

import aiohttp
from pytdbot import Client, types

from src.core import Filter

__mod_name__ = "GitHub"
__help__ = """
<b>GitHub Commands:</b>

• <code>/github [username]</code> — Get GitHub user info
"""


@Client.on_message(filters=Filter.command("github"))
async def github_cmd(c: Client, message: types.Message) -> None:
    text = message.text or ""
    parts = text.split(None, 1)
    if len(parts) < 2:
        reply = await message.reply_text("Usage: <code>/github [username]</code>")
        if isinstance(reply, types.Error):
            c.logger.warning(f"github_cmd error: {reply.message}")
        return

    username = parts[1].strip()
    msg = await message.reply_text(
        f"🔍 Fetching GitHub info for <b>{html.escape(username)}</b>..."
    )
    if isinstance(msg, types.Error):
        return

    try:
        url = f"https://api.github.com/users/{username}"
        async with aiohttp.ClientSession() as session:
            headers = {"Accept": "application/vnd.github.v3+json"}
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 404:
                    await msg.edit_text(
                        f"❌ User <b>{html.escape(username)}</b> not found on GitHub."
                    )
                    return
                if resp.status != 200:
                    await msg.edit_text(f"❌ GitHub API error (status {resp.status}).")
                    return
                data = await resp.json()

        login = data.get("login", "N/A")
        name = data.get("name", "N/A")
        bio = data.get("bio", "No bio")
        public_repos = data.get("public_repos", 0)
        followers = data.get("followers", 0)
        following = data.get("following", 0)
        company = data.get("company", "N/A")
        location = data.get("location", "N/A")
        blog = data.get("blog", "")
        created = data.get("created_at", "N/A")[:10]
        avatar = data.get("avatar_url", "")
        profile_url = data.get("html_url", f"https://github.com/{username}")

        result = (
            f"🧑‍💻 <b>GitHub: {html.escape(name or login)}</b>\n\n"
            f"<b>Username:</b> <code>{html.escape(login)}</code>\n"
            f"<b>Bio:</b> {html.escape(str(bio)[:200] if bio else 'N/A')}\n"
            f"<b>Public Repos:</b> <code>{public_repos}</code>\n"
            f"<b>Followers:</b> <code>{followers}</code>\n"
            f"<b>Following:</b> <code>{following}</code>\n"
            f"<b>Company:</b> <code>{html.escape(str(company))}</code>\n"
            f"<b>Location:</b> <code>{html.escape(str(location))}</code>\n"
            f"<b>Joined:</b> <code>{created}</code>\n"
        )

        if blog:
            result += (
                f'<b>Blog:</b> <a href="{html.escape(blog)}">{html.escape(blog)}</a>\n'
            )

        result += f'\n<a href="{profile_url}">View Profile</a>'

        await msg.edit_text(result, disable_web_page_preview=True)

    except Exception as e:
        await msg.edit_text(f"❌ Error: <code>{html.escape(str(e))}</code>")
