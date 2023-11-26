import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
FM_API_KEY = os.getenv("LASTFM_API_KEY")
PREFIX = os.getenv("PREFIX", "fmbot")

TEST_GUILDS = [int(x) for x in os.getenv("TEST_GUILDS", "").split(",") if x.isdigit()]
