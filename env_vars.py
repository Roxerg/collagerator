import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
FM_API_KEY = os.getenv("LASTFM_API_KEY")
APP_ID = os.getenv("APP_ID")
GUILD_IDS = [int(guild) for guild in os.getenv("GUILDS").split(",")]
