# bot.py
import os

import discord

from env_vars import TOKEN

client = discord.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        print(guild.name)
        print(guild.id + 1)


client.run(TOKEN)
