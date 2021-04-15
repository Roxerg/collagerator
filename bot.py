# bot.py
import os

import discord
from dotenv import load_dotenv

import json

#import requests
import grequests

from PIL import Image
from io import BytesIO

import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
FM_API_KEY = os.getenv('LASTFM_API_KEY')



class CustomClient(discord.Client):

    def __init__(self):
        super().__init__()
        self.BOT_CALL = "fmbot"
        self.query_albums = "https://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user={}&api_key={}&format=json&period={}&limit={}"
        self.intervals = ["overall", "7day", "1month", "3month",  "6month", "12month"]
        self.commands  = ["list", "collage", "<width>x<height>"]

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        guild = discord.utils.get(self.guilds, name=GUILD)

        print(
            f'{self.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})')

    def error_msg(self):
        response = "Something went wrong. Command format is:\n`{} <command> <last.fm username> <period>`\ncommands can be: {}\nperiod can be: {}".format(self.BOT_CALL, " | ".join(self.commands)," | ".join(self.intervals))
        return response


    async def on_message(self, message):
        if message.author == self.user:
            return
        
        words = message.content.split(" ")

        if self.BOT_CALL+"++" in message.content or self.BOT_CALL+" ++" in message.content:
            await message.channel.send("OwO wot's dis? thanx for kawmas >w<")
            return 

        if words[0] != self.BOT_CALL:
            return        
    
        try:
            command,username = words[1:3]
        except:
            await message.channel.send(self.error_msg())
            return

        period = words[3] if len(words) > 3 else "7day"

        if period not in self.intervals:
            if period == "month":
                period = "1month"
            elif period == "week":
                period = "7day"
            else:
                print("period failed")
                await message.channel.send(self.error_msg())
                return

        if command == "list":
            await self.top_list(username, period, message)
        elif command == "collage":
            await self.top_collage(username, period, message)
        elif re.match("^[0-9]x[0-9]$", command):
            await self.top_collage(username, period, message, dims=command)
        else:
            print("command failed")
            await message.channel.send(self.error_msg())
            return
        

    async def top_list(self, username, period, message):

        rqs = [ grequests.get(self.query_albums.format(username, FM_API_KEY, period, 6)) ]
        responses = grequests.map(rqs)
        res = responses[0].json()

        try:
            top_albums = [ album["name"] for album in res["topalbums"]["album"] ][0:5]
        except:
            response = "no albums found for user {} :pensive:".format(username)
            await message.channel.send(response)

        if len(top_albums) == 0:
            response = "no albums found for user {} :pensive:".format(username)
            await message.channel.send(response)

        
        if username[-1] == "s":
            username = username + "'"
        else:
            username = username + "'s"

        response = "{} top albums are:\n{}".format(username, "\n".join(top_albums))
        await message.channel.send(response)

    async def top_collage(self, username, period, message, dims="3x3"):

        by_x, by_y = [int(x) for x in dims.split("x")]


        rqs =[ grequests.get(self.query_albums.format(username, FM_API_KEY, period, by_x*by_y)) ]
        responses = grequests.map(rqs)
        res = responses[0].json()

        try:
            top_albums = [ album["image"][2]["#text"] for album in res["topalbums"]["album"] ]
            if len(top_albums) != len(res["topalbums"]["album"]):
                response = "huh i couldn't grab all the images i needed"
                await message.channel.send(response)

        except:
            response = "no albums found for user {} :pensive:".format(username)
            await message.channel.send(response)
            return

        if len(top_albums) == 0:
            response = "no albums found for user {} :pensive:".format(username)
            await message.channel.send(response)
            return

        if by_x + by_y > len(top_albums):
            response = "you don't have enough albums in that period for a {}x{} collage, bucko".format(by_x, by_y)
            await message.channel.send(response)
            return

        
        rqs = (grequests.get(album) for album in top_albums)
        responses = grequests.map(rqs)    
        
        images = [Image.open(BytesIO(r.content)) for r in responses]

        width, height = images[0].size

        

        canvas = Image.new(
                    mode = "RGB",
                    size = (by_x*width,by_y*height) )

        i = 0
        for y in range(0,by_y):
            for x in range(0, by_x):
                canvas.paste(images[i], (x*width, y*height))
                i += 1

        final = canvas

        with BytesIO() as image_binary:
            final.save(image_binary, 'PNG')
            image_binary.seek(0)
            await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))



client = CustomClient()
client.run(TOKEN)