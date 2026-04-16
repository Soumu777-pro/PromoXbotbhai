from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
from utils import load, save
from userbot import start_userbot, stop_all

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

login_state = {}


# ================= SUDO CHECK =================
def is_sudo(uid):
    data = load()
    return uid == OWNER_ID or uid in data.get("sudo", [])


# ================= START =================
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("🔥 Bot Online")


# ================= HELP =================
@bot.on(events.NewMessage(pattern="/help"))
async def help(event):
    await event.reply("""
/login
/list
/active <id>
/on
/off
.auto on/off
.delay <sec>
.dp <sec>
/sudo add/remove/list
""")


# ================= LOGIN =================
@bot.on(events.NewMessage(pattern="/login"))
async def login(event):
    login_state[event.sender_id] = {"step": "phone"}
    await event.reply("📱 Send phone number")


@bot.on(events.NewMessage)
async def login_flow(event):
    uid = event.sender_id

    if uid not in login_state:
        return

    state = login_state[uid]

    # PHONE
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

    # OTP
    elif state["step"] == "otp":
        otp = event.raw_text
        client = state["client"]

        try:
            await client.sign_in(
                state["phone"],
                otp,
                phone_code_hash=state["hash"]
            )
        except Exception as e:
            if "password" in str(e).lower():
                state["step"] = "2fa"
                await event.reply("🔐 Enter 2FA password")
                return
            await event.reply(f"❌ Error: {e}")
            return

        session = client.session.save()
        data = load()

        sid = str(len(data["sessions"]) + 1)
        data["sessions"][sid] = {"session": session, "active": False}

        save(data)

        await event.reply(f"✅ Session saved {sid}")
        login_state.pop(uid)

    # 2FA
    elif state["step"] == "2fa":
        password = event.raw_text
        client = state["client"]

        try:
            await client.sign_in(password=password)
        except Exception as e:
            return await event.reply(f"❌ 2FA Error: {e}")

        session = client.session.save()
        data = load()

        sid = str(len(data["sessions"]) + 1)
        data["sessions"][sid] = {"session": session, "active": False}

        save(data)

        await event.reply(f"🔐 2FA Done → {sid}")
        login_state.pop(uid)


# ================= LIST =================
@bot.on(events.NewMessage(pattern="/list"))
async def list_sessions(event):
    data = load()

    msg = ""
    for k, v in data.get("sessions", {}).items():
        msg += f"{k}. Active={v['active']}\n"

    await event.reply(msg or "No sessions")


# ================= ACTIVE =================
@bot.on(events.NewMessage(pattern=r"/active (\d+)"))
async def active(event):
    if not is_sudo(event.sender_id):
        return await event.reply("❌ Not allowed")

    sid = event.pattern_match.group(1)
    data = load()

    if sid not in data["sessions"]:
        return await event.reply("❌ Invalid session")

    data["sessions"][sid]["active"] = True
    save(data)

    await start_userbot(
        sid,
        data["sessions"][sid]["session"],
        API_ID,
        API_HASH
    )

    await event.reply(f"🔥 Session {sid} started")


# ================= ON =================
@bot.on(events.NewMessage(pattern="/on"))
async def on_all(event):
    if not is_sudo(event.sender_id):
        return await event.reply("❌ Not allowed")

    data = load()

    for sid, s in data.get("sessions", {}).items():
        if s["active"]:
            await start_userbot(sid, s["session"], API_ID, API_HASH)

    await event.reply("✅ All ON")


# ================= OFF =================
@bot.on(events.NewMessage(pattern="/off"))
async def off_all(event):
    if not is_sudo(event.sender_id):
        return await event.reply("❌ Not allowed")

    await stop_all()
    await event.reply("🛑 All OFF")


# ================= AUTO BROADCAST =================
@bot.on(events.NewMessage(pattern=r"\.auto on"))
async def auto_on(event):
    if not is_sudo(event.sender_id):
        return

    data = load()
    data["settings"]["auto"] = True
    save(data)

    await event.reply("🔥 Auto Broadcast ON")


@bot.on(events.NewMessage(pattern=r"\.auto off"))
async def auto_off(event):
    if not is_sudo(event.sender_id):
        return

    data = load()
    data["settings"]["auto"] = False
    save(data)

    await event.reply("🛑 Auto Broadcast OFF")


# ================= DELAY =================
@bot.on(events.NewMessage(pattern=r"\.delay (\d+)"))
async def set_delay(event):
    if not is_sudo(event.sender_id):
        return

    val = int(event.pattern_match.group(1))
    data = load()

    data["settings"]["delay"] = val
    save(data)

    await event.reply(f"⏱ Delay set {val}s")


# ================= DP =================
@bot.on(events.NewMessage(pattern=r"\.dp ([0-9.]+)"))
async def set_dp(event):
    if not is_sudo(event.sender_id):
        return

    val = float(event.pattern_match.group(1))
    data = load()

    data["settings"]["dp"] = val
    save(data)

    await event.reply(f"⚡ DP set {val}s")


# ================= SUDO =================
@bot.on(events.NewMessage(pattern=r"/sudo add (\d+)"))
async def sudo_add(event):
    if event.sender_id != OWNER_ID:
        return

    uid = int(event.pattern_match.group(1))
    data = load()

    if uid not in data["sudo"]:
        data["sudo"].append(uid)
        save(data)

    await event.reply(f"✅ Added sudo {uid}")


@bot.on(events.NewMessage(pattern=r"/sudo remove (\d+)"))
async def sudo_remove(event):
    if event.sender_id != OWNER_ID:
        return

    uid = int(event.pattern_match.group(1))
    data = load()

    if uid in data["sudo"]:
        data["sudo"].remove(uid)
        save(data)

    await event.reply(f"🗑 Removed sudo {uid}")


@bot.on(events.NewMessage(pattern="/sudo list"))
async def sudo_list(event):
    if not is_sudo(event.sender_id):
        return

    data = load()
    await event.reply("\n".join(map(str, data.get("sudo", []))) or "Empty")
