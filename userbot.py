from telethon import TelegramClient, events
from telethon.errors import YouBlockedUserError, FloodWaitError
import asyncio
import os

api_id_1 = int(os.environ["35288684"])
api_hash_1 = os.environ["44a65f5a5091d98cd5048301237ca8ee "]

api_id_2 = int(os.environ["32479322"])
api_hash_2 = os.environ["36b1f55abed381ee148331a29cb3e26"]

SESSION_DIR = os.environ.get("SESSION_DIR", "/data")


def attach_handlers(client, label):
    replied_users = set()

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if not event.is_private:
            return
        if event.out:
            return

        sender = await event.get_sender()
        user_id = sender.id if sender else None

        if user_id in replied_users:
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

            if user_id is not None:
                replied_users.add(user_id)

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


async def main():
    os.makedirs(SESSION_DIR, exist_ok=True)

    client1 = TelegramClient(
        os.path.join(SESSION_DIR, "session1"),
        api_id_1,
        api_hash_1,
        auto_reconnect=True,
        connection_retries=-1,
        retry_delay=5,
    )

    client2 = TelegramClient(
        os.path.join(SESSION_DIR, "session2"),
        api_id_2,
        api_hash_2,
        auto_reconnect=True,
        connection_retries=-1,
        retry_delay=5,
    )

    attach_handlers(client1, "Account 1")
    attach_handlers(client2, "Account 2")

    await client1.start()
    await client2.start()

    print("Both accounts are running...")

    await asyncio.gather(
        client1.run_until_disconnected(),
        client2.run_until_disconnected(),
    )


if __name__ == "__main__":
    asyncio.run(main())