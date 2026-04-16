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
        await event.reply(f"📊 Active Session ID: {sid}")


    # ================= .b BROADCAST =================
    @client.on(events.NewMessage(pattern=r"\.b (.+)"))
    async def broadcast(event):
        msg = event.pattern_match.group(1)

        data = load()
        dp = float(data.get("settings", {}).get("dp", 0.5))

        count = 0

        async for chat in client.iter_dialogs():
            try:
                await client.send_message(chat.id, msg)
                count += 1
                await asyncio.sleep(dp)
            except:
                continue

        await event.reply(f"📢 Sent to {count} chats")


    # ================= AUTO LOOP =================
    asyncio.create_task(auto_broadcast_loop(client))

    return client


# ================= AUTO BROADCAST LOOP =================
async def auto_broadcast_loop(client):
    while True:
        data = load()
        settings = data.get("settings", {})

        if not settings.get("auto"):
            await asyncio.sleep(5)
            continue

        msg = settings.get("auto_msg", "Hello")
        dp = float(settings.get("dp", 0.5))
        delay = int(settings.get("delay", 10))

        count = 0

        try:
            async for chat in client.iter_dialogs():
                try:
                    await client.send_message(chat.id, msg)
                    count += 1
                    await asyncio.sleep(dp)
                except:
                    continue
        except:
            pass

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
