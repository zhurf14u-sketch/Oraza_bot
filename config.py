import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TIMEZONE = "Asia/Almaty"

CITY = "Astana"
COUNTRY = "Kazakhstan"
METHOD = 3