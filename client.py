import re
from io import BytesIO
from typing import List
from urllib.parse import quote_plus

import discord
import grequests

import log_service
from env_vars import FM_API_KEY
from image_processing import ImageProcessor


from utils import duration_helper, get_meta


class CustomClient(discord.Client):
    def __init__(self, logger: log_service.LogService):
        super().__init__()

        self.BOT_CALL = "fmbot"
        self.log = logger

        self.query_tracks = "https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={}&api_key={}&format=json&period={}&limit={}"
        self.query_albums = "https://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user={}&api_key={}&format=json&period={}&limit={}"
        self.query_artists = "https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={}&api_key={}&format=json&period={}&limit={}"

        self.intervals = ["overall", "7day", "1month", "3month", "6month", "12month"]
        self.commands = ["artists", "albums", "tracks", "collage", "<width>x<height>"]

        self.imageProcessor = ImageProcessor()

    @property
    def guild_ids(self) -> List[int]:
        return list(map(lambda guild: guild.id, self.guilds))

    async def on_ready(self):
        print("{} is up and running UwU".format(self.user))
        print("Guilds Connected:")
        print([guild.name for guild in self.guilds])
        print(self.GUILD_IDS)

    def error_msg(self) -> str:
        response = "Something went wrong. type `{} help` for instructions.".format(self.BOT_CALL)
        return response

    def help_msg(self) -> str:
        response = "Command format:\n`{} <command> <last.fm username> <period>`\ncommands can be: `{}`\nperiod can be: `{}`\n(`period` and `username` are optional)".format(
            self.BOT_CALL, " | ".join(self.commands), " | ".join(self.intervals)
        )
        return response

    def validate(self, command: str, username: str, period: str) -> tuple[str, str, str]:

        username = quote_plus(username)

        return command, username, period

    async def on_message(self, message: discord.Message):

        period = None

        if message.author == self.user:
            return

        words = message.content.split(" ")

        if self.BOT_CALL + "++" in message.content or self.BOT_CALL + " ++" in message.content:
            await message.channel.send("OwO wot's dis? thanx for kawmas >w<")
            return

        if words[0] != self.BOT_CALL:
            return

        self.log.request_classic(message.content, message.author, {})

        if words[1] == "help":
            await message.channel.send(self.help_msg())
            return

        try:
            command, username = words[1:3]
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

        if re_type == BotResponseCode.ERROR or re_type == BotResponseCode.TEXT:
            await message.channel.send(response)
        elif re_type == BotResponseCode.IMAGE:
            await message.channel.send(file=discord.File(fp=response, filename="image.png"))

    async def top_list(
        self, username: str, period: str, thing: str = "albums", limit: int = 6
    ) -> tuple[BotResponseCode, str]:

        if thing == "albums":
            rqs = [grequests.get(self.query_albums.format(username, FM_API_KEY, period, limit))]
        elif thing == "artists":
            rqs = [grequests.get(self.query_artists.format(username, FM_API_KEY, period, limit))]
        else:
            rqs = [grequests.get(self.query_tracks.format(username, FM_API_KEY, period, limit))]

        responses = grequests.map(rqs)
        res = responses[0].json()

        try:
            if thing == "albums":
                top_albums = [
                    "{} by {} ({} plays)".format(album["name"], album["artist"]["name"], album["playcount"])
                    for album in res["topalbums"]["album"]
                ][0:limit]
            elif thing == "artists":
                top_albums = [
                    "{} ({} plays)".format(album["name"], album["playcount"]) for album in res["topartists"]["artist"]
                ][0:limit]
            else:
                top_albums = [
                    "{} by {} {} ({} plays)".format(
                        album["name"],
                        album["artist"]["name"],
                        duration_helper(album["duration"]),
                        album["playcount"],
                    )
                    for album in res["toptracks"]["track"]
                ][0:limit]
        except:
            response = "no albums found for user {} :pensive:".format(username)
            print(thing)
            print(res)
            return BotResponseCode.ERROR, response

        if len(top_albums) == 0:
            print(thing)
            print(res)
            response = "no albums found for user {} :pensive:".format(username)
            return BotResponseCode.ERROR, response

        if username[-1] == "s":
            username = username + "'"
        else:
            username = username + "'s"

        response = "{} top {} are:\n{}".format(username, thing, "\n".join(top_albums))
        return BotResponseCode.TEXT, response

    async def top_collage(
        self, username: str, period: str, dims: str = "3x3"
    ) -> tuple[BotResponseCode, str] or tuple[BotResponseCode, BytesIO]:

        by_x, by_y = [int(x) for x in dims.split("x")]

        rqs = [grequests.get(self.query_albums.format(username, FM_API_KEY, period, by_x * by_y))]
        responses = grequests.map(rqs)
        res = responses[0].json()

        try:
            top_albums = [get_meta(album) for album in res["topalbums"]["album"]]
            if len(top_albums) != len(res["topalbums"]["album"]):
                response = "huh i couldn't grab all the images i needed"
                return BotResponseCode.ERROR, response

        except:
            response = "no albums found for user {} :pensive:".format(username)
            return BotResponseCode.ERROR, response

        if len(top_albums) == 0:
            response = "no albums found for user {} :pensive:".format(username)
            return BotResponseCode.ERROR, response

        if by_x * by_y > len(top_albums):
            response = "you don't have enough albums in that period for a {}x{} collage, bucko".format(by_x, by_y)
            return BotResponseCode.ERROR, response

        rqs = (grequests.get(album["cover_url"]) for album in top_albums)
        responses = grequests.map(rqs)

        full_data = list(zip(responses, map(lambda a: a["info"], top_albums)))

        image_binary = self.imageProcessor.generate_collage_binary(full_data, by_x, by_y)

        return BotResponseCode.IMAGE, image_binary
