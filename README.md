# Discord ➜ Telegram Bridge

Forwards messages from a Discord channel to one or more Telegram groups/channels. Discord is the publisher; Telegram is the subscriber.

## How it works

- Each Discord channel (publisher) has a unique Publisher ID managed by an internal broker.
- Telegram chats (groups/channels) subscribe to that Publisher ID via a private chat with the Telegram bot.
- New messages in the Discord channel are forwarded to all subscribed Telegram chats (text + photos). `@everyone` is stripped.
- State (IDs, subscriptions, logs) is stored under `data/`.

## Requirements

- Configuration: set `DISCORD_BOT_TOKEN` and `TELEGRAM_BOT_TOKEN` (via `.env`, Compose env, or shell env).
- Discord:
  - Enable “Message Content Intent” in the Discord Developer Portal.
  - Bot permissions in the source channel: View Channel, Read Message History, Manage Messages (to delete command messages).
  - Commands are intended for server administrators.
- Telegram:
  - Add the bot as an admin in the destination group/channel (so it can delete `/id` and DM admins).
  - For channels, use `/id <admin_username>` so the bot knows whom to DM the chat ID.

## Commands

- Discord (admin in source channel):
  - `/id` — DM you the Publisher ID for this channel.
  - `/reset` — Rotate Publisher ID and remove all subscribers for this channel.
  - `/pause` — Pause publishing; `/resume` — resume.
- Telegram:
  - In group/channel: `/id` (or `/id <admin_username>` in channels) — DM the chat ID and delete the command message.
  - In private chat with the bot: `/sub <publisher_id> <chat_id>`, `/reset` (unsubscribe this user from all publishers).

## Setup and run

1) Create `.env` in the project root:

```
DISCORD_BOT_TOKEN=your_discord_bot_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

2) Run with Docker Compose:

```
docker compose up --build -d
```

   - Persists data and logs in `./data`.
3) Or run locally (Python 3.12+, Poetry):

```
poetry install
poetry run bot start          # normal
poetry run bot -d start       # debug logging
```

## Quick usage

1) In the Discord source channel, an admin runs `/id` to receive the Publisher ID via DM.
2) In the Telegram destination:
   - Group: run `/id` to receive the chat ID via DM.
   - Channel: run `/id <admin_username>` so the bot can DM that admin the chat ID.
3) In a private chat with the Telegram bot, send `/sub <publisher_id> <chat_id>`.

To stop forwarding:
- Discord: `/reset` (drops all subscribers by rotating the Publisher ID).
- Telegram (private): `/reset` (unsubscribes this user from all publishers).

## Notes

- One-way bridge: Discord ➜ Telegram. Sending with the Discord bot is intentionally disabled.
- Images: Each Discord image is forwarded to Telegram with the message text as caption.
- Entrypoint: `poetry run bot start` (Typer CLI at `bot/main.py`). Storage is JSON under `data/` (e.g., `brokage.json`).

## Troubleshooting

- Discord bot not receiving messages? Ensure Message Content Intent is enabled and the bot has channel permissions noted above.
- No DM for `/id`? Confirm the caller is an admin and DMs from the bot are allowed.
- For Telegram channels, always use `/id <admin_username>` so the bot knows who to DM.
