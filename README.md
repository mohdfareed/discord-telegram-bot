# Discord Telegram Bot

A lightweight bot that forwards messages from a Discord channel to a Telegram channel.

## Usage

- **Chat IDs:**
  - Chats (like Discord channels and Telegram groups) have a unique chat ID.
  - Admins can get this by using `/get_id` (sent via private message).

- **Subscription:**
  - In a subscriber bot's private chat, use:
    `/sub <subscriberID> <publisherID>`
    to forward messages from the publisher to the subscriber.
    The IDs are obtained using `/get_id`.
  - A single subscriber bot can subscribe to multiple publisher bots.

- **Supported Bots Commands:**
  - **Discord (publisher):**
    - `/get_id` — Gets the chat ID of the channel.
    - `/reset_id` — Resets the chat ID and disconnects all subscribers.
  - **Telegram (subscriber):**
    - `/get_id` — Gets the chat ID of the group/chat.
    - `/subs` — Lists all subscribed chat IDs.
    - `/unsub` — Unsubscribes from all publishers.
    - `/sub <subID> <pubID>` — Subscribes a chat to a publisher.

## Installation

**Bots Links:**

- [Telegram Bot](t.me/discord_telegram_forward_bot)
- [Discord Bot](https://discord.com/oauth2/authorize?client_id=1348406687706517594)
