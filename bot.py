# bot.py
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction

from params.env_vars import (
    TOKEN,
    PREFIX,
    TEST_GUILDS,
)

from services.log_service import LogService
from services.log_service import BotResponseCode

from services.collage_service import CollageService



from params.slash_options import (
    DimensionsOption,
    UsernameOption,
    CountOption,
    ListOption,
    PeriodOption,
)

from controllers import SlashController
from controllers import PrefixController

DiscordContext = commands.Context

log = LogService()
service = CollageService(log)
slash_controller = SlashController(service, log)
prefix_controller = PrefixController(service, log)

intents = disnake.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, test_guilds=TEST_GUILDS, intents=intents)

# i hate that i have to do this
prefix_controller.set_user(bot.user)

### SLASH COMMANDS ### 
@bot.slash_command(name="ping")
async def _ping(inter: ApplicationCommandInteraction):
    await inter.response.send_message(content="Pong! ({}ms)".format(bot.latency * 1000))

@bot.slash_command(
    name="collage",
    description="Generates a collage out of your most listened album covers!",
    options=[UsernameOption, DimensionsOption, PeriodOption]
)
async def _collage(inter: ApplicationCommandInteraction, username: str = "", dimensions: str = "3x3", period: str = "7day"):
    await slash_controller.collage(inter, username, dimensions, period)

@bot.slash_command(
    name="list",
    description="Provides a list of your most listened songs/artists/albums",
    options=[UsernameOption, ListOption, PeriodOption, CountOption],
)
async def _list(inter: ApplicationCommandInteraction, username: str = "", period: str = "7day", listof: str = "albums", count: str = 5):
    await slash_controller.toplist(inter, username, period, listof, count)

### PREFIX COMMANDS ###
### TODO: ideally split similarly to slash_commands
### if disnake allows it

@bot.event
async def on_message(msg: disnake.Message):
    await prefix_controller.on_message(msg)


bot.run(TOKEN)

