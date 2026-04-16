import asyncio
from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
from utils import load, save
from userbot import start_userbot, stop_all, clients

bot = TelegramClient("bot", API_ID, API_HASH)

login_state = {}

def is_sudo(uid):
    data = load()
    return uid == OWNER_ID or uid in data.get("sudo", [])

# ---------------- START ----------------
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("🔥 Bot Online")

# ---------------- HELP ----------------
@bot.on(events.NewMessage(pattern="/help"))
async def help(event):
    await event.reply("""
/login
/list
/active <id>
/on
/off
.auto on/off
.setmsg <text>
/b (reply)
.delay
.dp
.max
.batch on/off
""")

# ---------------- LOGIN (UNCHANGED CORE) ----------------
@bot.on(events.NewMessage(pattern="/login"))
async def login(event):
    login_state[event.sender_id] = {"step": "phone"}
    await event.reply("📱 Send phone")

@bot.on(events.NewMessage)
async def login_flow(event):
    uid = event.sender_id

    if uid not in login_state:
        return

    state = login_state[uid]

    if state["step"] == "phone":
        phone = event.raw_text

        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()

        sent = await client.send_code_request(phone)

        state.update({
            "step": "otp",
            "phone": phone,
            "client": client,
            "hash": sent.phone_code_hash
        })

        await event.reply("📩 OTP sent")

    elif state["step"] == "otp":
        otp = event.raw_text
        client = state["client"]

        try:
            await client.sign_in(state["phone"], otp, phone_code_hash=state["hash"])
        except:
            state["step"] = "2fa"
            await event.reply("🔐 2FA password?")
            return

        session = client.session.save()
        data = load()

        sid = str(len(data["sessions"]) + 1)
        data["sessions"][sid] = {"session": session, "active": False}
        save(data)

        await event.reply(f"✅ Saved {sid}")
        login_state.pop(uid)

# ---------------- SESSION ----------------
@bot.on(events.NewMessage(pattern="/list"))
async def list_sessions(event):
    data = load()
    await event.reply(str(data["sessions"]))

@bot.on(events.NewMessage(pattern=r"/active (\d+)"))
async def active(event):
    if not is_sudo(event.sender_id):
        return

    sid = event.pattern_match.group(1)
    data = load()

    data["sessions"][sid]["active"] = True
    save(data)

    await start_userbot(sid, data["sessions"][sid]["session"], API_ID, API_HASH)
    await event.reply("🔥 Started")

@bot.on(events.NewMessage(pattern="/on"))
async def on(event):
    if not is_sudo(event.sender_id):
        return

    data = load()

    for sid, s in data["sessions"].items():
        if s["active"]:
            await start_userbot(sid, s["session"], API_ID, API_HASH)

    await event.reply("✅ ON")

@bot.on(events.NewMessage(pattern="/off"))
async def off(event):
    if not is_sudo(event.sender_id):
        return

    await stop_all()
    await event.reply("🛑 OFF")

# ---------------- AUTO ----------------
@bot.on(events.NewMessage(pattern=r"\.auto on"))
async def auto_on(event):
    data = load()
    data["settings"]["auto"] = True
    save(data)
    await event.reply("🔥 Auto ON")

@bot.on(events.NewMessage(pattern=r"\.auto off"))
async def auto_off(event):
    data = load()
    data["settings"]["auto"] = False
    save(data)
    await event.reply("🛑 Auto OFF")

# ---------------- SET MSG ----------------
@bot.on(events.NewMessage(pattern=r"\.setmsg (.+)"))
async def setmsg(event):
    if not is_sudo(event.sender_id):
        return

    msg = event.pattern_match.group(1)
    data = load()

    data["settings"]["broadcast_msgs"].append(msg)
    save(data)

    await event.reply("✅ Added")

# ---------------- CLEAR MSG ----------------
@bot.on(events.NewMessage(pattern=r"\.clearmsg"))
async def clear(event):
    data = load()
    data["settings"]["broadcast_msgs"] = []
    save(data)
    await event.reply("🗑 Cleared")

# ---------------- /b BROADCAST ----------------
@bot.on(events.NewMessage(pattern="/b"))
async def broadcast(event):
    if not is_sudo(event.sender_id):
        return

    if not event.is_reply:
        return await event.reply("Reply to message")

    msg = (await event.get_reply_message()).text

    count = 0

    for c in clients.values():
        async for d in c.iter_dialogs():
            try:
                await c.send_message(d.id, msg)
                count += 1
            except:
                continue

    await event.reply(f"⚡ Sent {count}")

# ---------------- CONTROL COMMANDS ----------------
@bot.on(events.NewMessage(pattern=r"\.delay (\d+)"))
async def delay(event):
    if not is_sudo(event.sender_id):
        return
    data = load()
    data["settings"]["delay"] = int(event.pattern_match.group(1))
    save(data)
    await event.reply("⏱ Updated")

@bot.on(events.NewMessage(pattern=r"\.dp ([0-9.]+)"))
async def dp(event):
    if not is_sudo(event.sender_id):
        return
    data = load()
    data["settings"]["dp"] = float(event.pattern_match.group(1))
    save(data)
    await event.reply("⚡ DP updated")

@bot.on(events.NewMessage(pattern=r"\.max (\d+)"))
async def maxx(event):
    if not is_sudo(event.sender_id):
        return
    data = load()
    data["settings"]["max"] = int(event.pattern_match.group(1))
    save(data)
    await event.reply("📦 Max set")

@bot.on(events.NewMessage(pattern=r"\.batch (on|off)"))
async def batch(event):
    if not is_sudo(event.sender_id):
        return
    data = load()
    data["settings"]["batch"] = event.pattern_match.group(1) == "on"
    save(data)
    await event.reply("⚙ Batch updated")

# ---------------- MAIN ----------------
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("🔥 BOT STARTED")
    await bot.run_until_disconnected()

asyncio.run(main())
