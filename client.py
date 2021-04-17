
import re

import grequests
import discord

from urllib.parse import quote_plus
from PIL import Image
from io import BytesIO

import env_vars

from env_vars import FM_API_KEY
from env_vars import GUILD_IDS

class CustomClient(discord.Client):

    def __init__(self):
        super().__init__()
        
        self.BOT_CALL = "fmbot"

        self.GUILD_IDS = GUILD_IDS

        self.query_tracks = "https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={}&api_key={}&format=json&period={}&limit={}"
        self.query_albums  = "https://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user={}&api_key={}&format=json&period={}&limit={}"
        self.query_artists = "https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={}&api_key={}&format=json&period={}&limit={}"
        
        self.intervals = ["overall", "7day", "1month", "3month",  "6month", "12month"]
        self.commands  = ["artists", "albums", "tracks", "collage", "<width>x<height>"]

    async def on_ready(self):
        print("{} is up and running UwU".format(self.user))
        self.GUILD_IDS = [guild.id for guild in self.guilds]
        print("Guilds Connected:")
        print([guild.name for guild in self.guilds])
        print(self.GUILD_IDS)
        

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
            elif period == "year":
                period = "12month"
            else:
                print("period failed")
                await message.channel.send(self.error_msg())
                return

        if command == "albums":
            re_type, response = await self.top_list(username, period, thing="albums")
        elif command == "artists":
            re_type, response = await self.top_list(username, period, thing="artists")
        elif command == "tracks":
            re_type, response = await self.top_list(username, period, thing="tracks")
        elif command == "collage":
            re_type, response = await self.top_collage(username, period)
        elif re.match("^[0-9]x[0-9]$", command):
            re_type, response = await self.top_collage(username, period, dims=command)
        else:
            print("command failed")
            await message.channel.send(self.error_msg())
            return

        if re_type == 0:
            await message.channel.send(response)
        elif re_type == 1:
            await message.channel.send(file=discord.File(fp=response, filename='image.png'))

    def duration_helper(self, duration):
        
        if int(duration) == 0:
            return ""

        mins = str(int(int(duration)/60))
        secs = str(int(int(duration)%60))

        mins = "0"*(2-len(mins))+mins
        secs = "0"*(2-len(secs))+secs

        return "({}:{})".format(mins,secs)

    async def top_list(self, username, period, thing="albums", limit=6):
        
        if thing == "albums":
            rqs = [ grequests.get(self.query_albums.format(username, FM_API_KEY, period, limit)) ]
        elif thing == "artists":
            rqs = [ grequests.get(self.query_artists.format(username, FM_API_KEY, period, limit)) ]
        else: 
            rqs = [ grequests.get(self.query_tracks.format(username, FM_API_KEY, period, limit)) ]

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
        # returns all black square if image could not be loaded
        res = Image.new(
                    mode = "RGB",
                    size = (174,174),
                    color=(0,0,0) )
        try:
            res = Image.open(BytesIO(r.content))
        except:
            pass
        return res

    async def top_collage(self, username, period, dims="3x3"):

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

        #with BytesIO() as image_binary:
        image_binary = BytesIO()
        final.save(image_binary, 'PNG')
        image_binary.seek(0)
        #await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
        return 1, image_binary


custom_client = CustomClient()