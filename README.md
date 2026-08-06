# MelodyForgeBot

MelodyForgeBot is a Telegram music and group-management bot for voice chats. The repository is maintained at https://github.com/themukeshdev/MelodyForgeBot.

It supports playback from YouTube, Spotify, JioSaavn, Apple Music and SoundCloud, and is designed to run reliably on Heroku, Docker and Linux VPS hosts.

## Features

- Voice chat playback with queue controls
- Multi-session assistant support
- MongoDB-backed configuration and logging
- Docker, Heroku and VPS deployment support
- Optional cookies and proxy support for streaming services

## Requirements

Before deploying, make sure you have:

- Python 3.10 or newer
- FFmpeg installed
- A MongoDB instance
- Telegram API credentials from my.telegram.org
- A bot token from @BotFather
- At least one Pyrogram session string

## Heroku deployment

### Deploy via Button

Use the button below to deploy this repository directly to Heroku. Our `app.json` is fully configured to automatically set up the required Python and FFmpeg buildpacks.

[![Deploy on Heroku](https://img.shields.io/badge/Deploy%20on%20Heroku-430098?style=for-the-badge&logo=heroku)](https://heroku.com/deploy?template=https://github.com/themukeshdev/MelodyForgeBot)

**Setup steps:**
1. Click the button above.
2. Fill in the required environment variables such as API_ID, API_HASH, TOKEN, STRING1 and MONGO_URI.
3. Deploy the app.
4. Heroku will automatically use the `requirements.txt` and `Procfile` to start the bot.

### Deploy via Heroku CLI

If you prefer using the command line:

```bash
heroku login
heroku create my-melody-bot
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
git push heroku main
heroku ps:scale worker=1
```
## VPS / Linux server deployment

### 1) Server preparation

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip python3-venv ffmpeg tmux curl
```

### 2) Clone and configure

```bash
git clone https://github.com/themukeshdev/MelodyForgeBot.git
cd MelodyForgeBot
cp sample.env .env
nano .env
```

Fill in the required values in .env before starting the bot.

### 3) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install uv
uv sync
```

### 4) Start the bot

Use tmux so the process keeps running after logout:

```bash
tmux new -s melodyforgebot
source .venv/bin/activate
uv run start
```

To detach, press Ctrl+B then D.

### 5) Restart or update

```bash
tmux attach -t melodyforgebot
# stop the bot with Ctrl+C
cd MelodyForgeBot
git pull
source .venv/bin/activate
uv sync
uv run start
```

## Local host / test run

To test the bot locally before deploying:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install uv
uv sync
cp sample.env .env
nano .env
uv run start
```

For Windows PowerShell, use:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install uv
uv sync
Copy-Item sample.env .env
notepad .env
uv run start
```

## Docker deployment

```bash
docker build -t melodyforgebot .
docker run -d --name melodyforgebot --env-file .env --restart unless-stopped melodyforgebot
```

## Important startup note

This project exposes the startup entrypoint through the package script. The recommended commands are:

- Heroku: Procfile worker process
- VPS: `uv run start`
- Alternative: `python -m src`

## Configuration highlights

The most important variables are:

- API_ID
- API_HASH
- TOKEN
- STRING1 (required)
- MONGO_URI
- OWNER_ID
- LOGGER_ID

## License

AGPL-3.0
