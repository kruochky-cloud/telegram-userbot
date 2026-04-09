from telethon import TelegramClient, events
from telethon.errors import (
    YouBlockedUserError,
    FloodWaitError,
    AuthKeyDuplicatedError,
)
from telethon.sessions import StringSession
import asyncio
import os
import time

api_id_1 = int(os.environ["API_ID_1"])
api_hash_1 = os.environ["API_HASH_1"]
session_1 = os.environ["SESSION_1"]

api_id_2 = int(os.environ["API_ID_2"])
api_hash_2 = os.environ["API_HASH_2"]
session_2 = os.environ["SESSION_2"]

REPLY_COOLDOWN_SECONDS = 24 * 60 * 60


def attach_handlers(client, label):
    replied_users = {}

    def cleanup_old_users():
        now = time.time()
        expired = [
            user_id for user_id, ts in replied_users.items()
            if now - ts >= REPLY_COOLDOWN_SECONDS
        ]
        for user_id in expired:
            del replied_users[user_id]

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if not event.is_private or event.out:
            return

        sender = await event.get_sender()
        user_id = sender.id if sender else None
        if user_id is None:
            return

        cleanup_old_users()

        last_replied_at = replied_users.get(user_id)
        if last_replied_at and (time.time() - last_replied_at) < REPLY_COOLDOWN_SECONDS:
            print(f"{label}: skipped {user_id} (already replied within 24h)")
            return

        reply_message = (
            "👋✨ Welcome!\n\n"
            "Hello! The account owner is busy now. Please be patient and wait!\n\n"
            "您好！用户在忙碌中，请耐心稍等！\n\n"
            "សួស្ដីបាទ! ម្ចាស់គណនីកំពុងជាប់រវល់។ សូមអត់ធ្មត់រង់ចាំ!"
        )

        try:
            await asyncio.sleep(3)
            await event.reply(reply_message)
            replied_users[user_id] = time.time()
            print(f"{label}: replied to {user_id}")

        except YouBlockedUserError:
            print(f"{label}: blocked user -> {user_id}")

        except FloodWaitError as e:
            print(f"{label}: flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except OSError as e:
            print(f"{label}: network error -> {e}")

        except Exception as e:
            print(f"{label}: unexpected error -> {e}")


async def run_account(label, api_id, api_hash, session):
    while True:
        client = None
        try:
            client = TelegramClient(
                StringSession(session),
                api_id,
                api_hash,
                auto_reconnect=True,
                connection_retries=-1,
                retry_delay=5,
            )

            attach_handlers(client, label)

            print(f"{label}: starting client...")
            await client.start()
            print(f"{label}: connected")

            await client.run_until_disconnected()
            print(f"{label}: disconnected, retrying in 5s...")

        except AuthKeyDuplicatedError:
            print(
                f"{label}: session invalid because it was used from multiple IPs. "
                f"Generate a new session string and use it in only one place."
            )
            break

        except OSError as e:
            print(f"{label}: connection/network error -> {e}. Retrying in 5s...")

        except Exception as e:
            print(f"{label}: fatal error -> {e}. Retrying in 5s...")

        finally:
            if client:
                try:
                    await client.disconnect()
                except Exception:
                    pass

        await asyncio.sleep(5)


async def main():
    await asyncio.gather(
        run_account("Account 1", api_id_1, api_hash_1, session_1),
        run_account("Account 2", api_id_2, api_hash_2, session_2),
    )


if __name__ == "__main__":
    asyncio.run(main())