# bot.py
import os

import discord
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice

from dotenv import load_dotenv

import json

#import requests
import grequests

from PIL import Image
from io import BytesIO

import re
from urllib.parse import quote_plus


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
FM_API_KEY = os.getenv('LASTFM_API_KEY')
APP_ID = os.getenv('APP_ID')



class CustomClient(discord.Client):

    def __init__(self):
        super().__init__()
        self.BOT_CALL = "fmbot"
        
        self.query_tracks = "https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={}&api_key={}&format=json&period={}&limit={}"
        self.query_albums  = "https://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user={}&api_key={}&format=json&period={}&limit={}"
        self.query_artists = "https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={}&api_key={}&format=json&period={}&limit={}"
        
        self.intervals = ["overall", "7day", "1month", "3month",  "6month", "12month"]
        self.commands  = ["artists", "albums", "tracks", "collage", "<width>x<height>"]

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        guild = discord.utils.get(self.guilds, name=GUILD)

        print(
            f'{self.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})')

    def error_msg(self):
        response = "Something went wrong. type `{} help` for instructions.".format(self.BOT_CALL)
        return response

    def help_msg(self):
        response = "Command format:\n`{} <command> <last.fm username> <period>`\ncommands can be: `{}`\nperiod can be: `{}`\n(`period` and `username` are optional)" \
                        .format(
                            self.BOT_CALL, 
                            " | ".join(self.commands),
                            " | ".join(self.intervals))
        return response


    def validate(self, command, username, period):
        
        username = quote_plus(username)

        return command, username, period

    async def on_message(self, message):

        period = None

        if message.author == self.user:
            return
        
        words = message.content.split(" ")

        if self.BOT_CALL+"++" in message.content or self.BOT_CALL+" ++" in message.content:
            await message.channel.send("OwO wot's dis? thanx for kawmas >w<")
            return 

        if words[0] != self.BOT_CALL:
            return        

        if words[1] == "help":
            await message.channel.send(self.help_msg())
            return    

    
        try:
            command,username = words[1:3]
            if username in self.intervals:
                period = username
                username, _ = message.author.name
        except:
            print("No username?")
            print("Try using: " + message.author.name)
            try:
                command = words[1:2][0]
                username = message.author.name
                print("username is: " + message.author.name)
            except:
                await message.channel.send(self.error_msg())
                return    


        if period == None:
            period = words[3] if len(words) > 3 else "7day"

        # make URL safe
        command, username, period = self.validate(command, username, period)

        if period not in self.intervals:
            if period == "month":
                period = "1month"
            elif period == "week":
                period = "7day"
            else:
                print("period failed")
                await message.channel.send(self.error_msg())
                return

        if command == "albums":
            re_type, response = await self.top_list(username, period, message, thing="albums")
        elif command == "artists":
            re_type, response = await self.top_list(username, period, message, thing="artists")
        elif command == "tracks":
            re_type, response = await self.top_list(username, period, message, thing="tracks")
        elif command == "collage":
            re_type, response = await self.top_collage(username, period, message)
        elif re.match("^[0-9]x[0-9]$", command):
            re_type, response = await self.top_collage(username, period, message, dims=command)
        else:
            print("command failed")
            await message.channel.send(self.error_msg())
            return

        if re_type == 0:
            message.channel.send(response)
        elif re_type == 1:
            message.channel.send(file=discord.File(fp=response, filename='image.png'))

    def duration_helper(self, duration):
        
        if int(duration) == 0:
            return ""

        mins = str(int(int(duration)/60))
        secs = str(int(int(duration)%60))

        mins = "0"*(2-len(mins))+mins
        secs = "0"*(2-len(secs))+secs

        return "({}:{})".format(mins,secs)



    async def top_list(self, username, period, message, thing="albums"):
        
        if thing == "albums":
            rqs = [ grequests.get(self.query_albums.format(username, FM_API_KEY, period, 6)) ]
        elif thing == "artists":
            rqs = [ grequests.get(self.query_artists.format(username, FM_API_KEY, period, 6)) ]
        else: 
            rqs = [ grequests.get(self.query_tracks.format(username, FM_API_KEY, period, 6)) ]

        responses = grequests.map(rqs)
        res = responses[0].json()

        try:
            if thing == "albums":
                top_albums = [ "{} by {} ({} plays)".format(album["name"], album["artist"]["name"], album["playcount"])
                                    for album in res["topalbums"]["album"] ][0:5]
            elif thing == "artists":
                top_albums = [ "{} ({} plays)".format(album["name"], album["playcount"])
                                    for album in res["topartists"]["artist"] ][0:5]
            else:
                top_albums = [ "{} by {} {} ({} plays)".format(
                                album["name"], 
                                album["artist"]["name"], 
                                self.duration_helper(album["duration"]),
                                album["playcount"])
                                    for album in res["toptracks"]["track"] ][0:5]
        except:
            response = "no albums found for user {} :pensive:".format(username)
            #await message.channel.send(response)
            return 0, response

        if len(top_albums) == 0:
            response = "no albums found for user {} :pensive:".format(username)
            #await message.channel.send(response)
            return 0, response

        
        if username[-1] == "s":
            username = username + "'"
        else:
            username = username + "'s"

        response = "{} top {} are:\n{}".format(username, thing, "\n".join(top_albums))
        #await message.channel.send(response)
        return 0, response

    def get_cover_link(self, album):
        res = None
        try:
            res = album["image"][2]["#text"]
        except:
            res = ""
        return res
    
    def get_cover(self, r):
        res = Image.new(
                    mode = "RGB",
                    size = (174,174),
                    color=(0,0,0) )
        try:
            res = Image.open(BytesIO(r.content))
        except:
            pass
        return res

    async def top_collage(self, username, period, message, dims="3x3"):

        by_x, by_y = [int(x) for x in dims.split("x")]


        rqs =[ grequests.get(self.query_albums.format(username, FM_API_KEY, period, by_x*by_y)) ]
        responses = grequests.map(rqs)
        res = responses[0].json()

        try:
            top_albums = [ self.get_cover_link(album) for album in res["topalbums"]["album"] ]
            if len(top_albums) != len(res["topalbums"]["album"]):
                response = "huh i couldn't grab all the images i needed"
                #await message.channel.send(response)
                return 0, response

        except:
            response = "no albums found for user {} :pensive:".format(username)
            #await message.channel.send(response)
            return 0, response

        if len(top_albums) == 0:
            response = "no albums found for user {} :pensive:".format(username)
            #await message.channel.send(response)
            return 0, response

        if by_x * by_y > len(top_albums):
            response = "you don't have enough albums in that period for a {}x{} collage, bucko".format(by_x, by_y)
            #await message.channel.send(response)
            return 0, response

        
        rqs = (grequests.get(album) for album in top_albums)
        responses = grequests.map(rqs)    
        
        images = [self.get_cover(r) for r in responses]

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
            #await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
            return 1, image_binary



client = CustomClient()
slash = SlashCommand(client, sync_commands=True)

guild_ids = [
    315277951597936640
]


@slash.slash(name="ping", guild_ids=guild_ids)
async def _ping(ctx): # Defines a new "context" (ctx) command called "ping."
    print("received!")
    await ctx.send(f"Pong! ({client.latency*1000}ms)")


@slash.slash(name="collage",
             description="Generates a collage out of your most listened album covers!",
             options=[
                create_option(
                 name="username",
                 description="Last.fm username. Defaults to Discord username.",
                 option_type=3,
                 required=False
               ),
               create_option(
                 name="dimensions",
                 description="format: <width>x<height>. goes up to 9x9. defaults to 3x3",
                 option_type=3,
                 required=False
               ),
               create_option(
                 name="period",
                 description="Data from what period of time. If nothing chosen, defaults to week",
                 option_type=3,
                 required=False,
                 choices=[
                  create_choice(
                    name="week",
                    value="7day"
                  ),
                  create_choice(
                    name="month",
                    value="1month"
                  ),
                  create_choice(
                    name="3month",
                    value="3month"
                  ),
                  create_choice(
                    name="6month",
                    value="6month"
                  ),
                  create_choice(
                    name="year",
                    value="12month"
                  ),
                  create_choice(
                    name="overall",
                    value="overall"
                  )
                ]
               )
             ])
async def _collage(ctx, username: str):
    print(username)
    pass

#client.run(TOKEN)