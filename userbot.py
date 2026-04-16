import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from utils import load

userbots = {}


# ================= START USERBOT =================
async def start_userbot(sid, session, api_id, api_hash):
    client = TelegramClient(StringSession(session), api_id, api_hash)
    await client.start()

    userbots[sid] = client

    print(f"✅ Userbot {sid} started")


    # ================= .ping =================
    @client.on(events.NewMessage(pattern=r"\.ping"))
    async def ping(event):
        await event.reply("🏓 Pong!")


    # ================= .stats =================
    @client.on(events.NewMessage(pattern=r"\.stats"))
    async def stats(event):
        await event.reply(f"📊 Session ID: {sid}")


    # ================= .b BROADCAST (FIXED) =================
    @client.on(events.NewMessage(pattern=r"\.b (.+)"))
    async def broadcast(event):
        msg = event.pattern_match.group(1)

        data = load()
        settings = data.get("settings", {})

        delay = int(settings.get("delay", 3))
        dp = float(settings.get("dp", 0))
        max_send = int(settings.get("max", 999))
        batch = settings.get("batch", False)

        final_delay = delay + dp

        count = 0

        if batch:
            tasks = []

            async for chat in client.iter_dialogs():
                if count >= max_send:
                    break

                tasks.append(client.send_message(chat.id, msg))
                count += 1

            await asyncio.gather(*tasks)
            await asyncio.sleep(final_delay)

        else:
            async for chat in client.iter_dialogs():
                if count >= max_send:
                    break

                try:
                    await client.send_message(chat.id, msg)
                    count += 1
                    await asyncio.sleep(final_delay)
                except:
                    continue

        await event.reply(f"📢 Sent to {count} chats")


    # ================= AUTO LOOP (FIXED ROTATION) =================
    asyncio.create_task(auto_broadcast_loop(client))

    return client


# ================= AUTO BROADCAST LOOP =================
async def auto_broadcast_loop(client):
    i = 0

    while True:
        data = load()
        settings = data.get("settings", {})

        if not settings.get("auto"):
            await asyncio.sleep(5)
            continue

        msgs = settings.get("broadcast_msgs", [])
        delay = int(settings.get("delay", 3))
        dp = float(settings.get("dp", 0))
        max_send = int(settings.get("max", 999))
        batch = settings.get("batch", False)

        if not msgs:
            await asyncio.sleep(5)
            continue

        msg = msgs[i % len(msgs)]
        i += 1

        final_delay = delay + dp

        count = 0

        if batch:
            tasks = []

            async for chat in client.iter_dialogs():
                if count >= max_send:
                    break

                tasks.append(client.send_message(chat.id, msg))
                count += 1

            await asyncio.gather(*tasks)
        else:
            async for chat in client.iter_dialogs():
                if count >= max_send:
                    break

                try:
                    await client.send_message(chat.id, msg)
                    count += 1
                    await asyncio.sleep(final_delay)
                except:
                    continue

        print(f"📢 Auto sent {count} chats")

        await asyncio.sleep(delay)


# ================= STOP ALL =================
async def stop_all():
    for c in userbots.values():
        try:
            await c.disconnect()
        except:
            pass

    userbots.clear()
