import os
from dotenv import load_dotenv

load_dotenv()

# ================= TELEGRAM API =================
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")

# ================= BOT =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ================= OWNER =================
OWNER_ID = int(os.getenv("OWNER_ID", 0))


# ================= VALIDATION (SAFE CHECK) =================
if not API_ID or not API_HASH or not BOT_TOKEN:
    print("❌ Missing API_ID / API_HASH / BOT_TOKEN in .env")
