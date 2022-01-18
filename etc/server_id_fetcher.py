
# Quick way of fetching guild IDs without running the main bot

import os
import sys
sys.path.insert(0,'.')

import disnake

from params.env_vars import TOKEN

client = disnake.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        print(guild.name)
        print(guild.id + 1)


client.run(TOKEN)
