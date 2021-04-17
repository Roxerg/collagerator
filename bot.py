# bot.py


from discord_slash import SlashCommand
import discord

from client import custom_client

from env_vars import TOKEN
from env_vars import GUILD_IDS

from slash_options import UsernameOption
from slash_options import DimensionsOption
from slash_options import PeriodOption
from slash_options import ListOption

slash = SlashCommand(custom_client, sync_commands=True)


@slash.slash(name="ping", guild_ids=custom_client.GUILD_IDS)
async def _ping(ctx):
    print("received!")
    await ctx.send(f"Pong! ({custom_client.latency*1000}ms)")


@slash.slash(name="collage", guild_ids=custom_client.GUILD_IDS,
             description="Generates a collage out of your most listened album covers!",
             options=[ UsernameOption, DimensionsOption, PeriodOption ])
async def _collage(ctx, username="", dimensions="3x3", period="7day"):
    await ctx.defer() # we do a little ACK so we have time to fetch stats
    username=str(username)
    
    if username == "":
        username = ctx.author.name

    re_type, response = await custom_client.top_collage(username, period, dims=dimensions)

    if re_type == 0:
        await ctx.send(response)
    elif re_type == 1:
        await ctx.send(file=discord.File(fp=response, filename='image.png'))


@slash.slash(name="list", guild_ids=custom_client.GUILD_IDS,
             description="Generates a collage out of your most listened album covers!",
             options=[ UsernameOption, ListOption, PeriodOption ])
async def _list(ctx, username="", period="7day", listof="albums", count=5):
    await ctx.defer() # we do a little ACK so we have time to fetch stats
    username=str(username)
    
    if username == "":
        username = ctx.author.name

    count = int(count) if int(count) <= 11 else 11

    re_type, response = await custom_client.top_list(username, period, thing=listof, limit=count)

    if re_type == 0:
        await ctx.send(response)
    elif re_type == 1:
        await ctx.send(file=discord.File(fp=response, filename='image.png'))


custom_client.run(TOKEN)









