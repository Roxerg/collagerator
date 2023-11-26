import re
from io import BytesIO
from typing import List
from urllib.parse import quote_plus

import disnake
import grequests

import services.log_service
from services.log_service import BotResponseCode
from services.log_service import LogService

from params.env_vars import FM_API_KEY
from params.env_vars import PREFIX

from image_processing import ImageProcessor

from services.collage_service import CollageService

from utils.utils import duration_helper, get_meta
from disnake.ext.commands import Bot

from disnake import ApplicationCommandInteraction

class SlashController():
    def __init__(self, service: CollageService, logger: LogService):
        self.service = service
        self.log = logger

    
    async def collage(self, inter: ApplicationCommandInteraction, username: str, dimensions: str, period: str):
        await inter.response.defer()  # we do a little ACK so we have time to fetch stats

        if username == "":
            username = inter.author.name

        self.log.request_slash(inter, "collage", username, extras={"dimensions": dimensions, "period": period})
        re_type, response, description = await self.service.top_collage(username, period, dims=dimensions)

        self.log.response("collage", username, re_type, response)
        if re_type == BotResponseCode.ERROR or re_type == BotResponseCode.TEXT:
            await inter.edit_original_message(content=response)
        elif re_type == BotResponseCode.IMAGE:
            await inter.edit_original_message(file=disnake.File(fp=response, filename="image.png"), content=description)


    async def toplist(self, inter: ApplicationCommandInteraction, username: str, period: str, listof: str, count: int):
        await inter.response.defer()  # we do a little ACK so we have time to fetch stats

        if username == "":
            username = inter.author.name

        count = count if count <= 11 else 11

        self.log.request_slash(
            inter,
            "list",
            username,
            extras={"listof": listof, "period": period, "count": count},
        )
        re_type, response = await self.service.top_list(username, period, thing=listof, limit=count)
        self.log.response("list", username, re_type, response)

        if re_type == BotResponseCode.ERROR or re_type == BotResponseCode.TEXT:
            await inter.edit_original_message(content=response)



class PrefixController():
    def __init__(self, service: CollageService, logger: LogService):
        self.service = service
        self.log = logger

        self.intervals = ["overall", "7day", "1month", "3month", "6month", "12month"]
        self.commands = ["artists", "albums", "tracks", "collage", "<width>x<height>"]

    def set_user(self, user):
        self.user = user

    def error_msg(self) -> str:
        response = "Something went wrong. type `{} help` for instructions.".format(PREFIX)
        return response

    def help_msg(self) -> str:
        response = "Command format:\n`{} <command> <last.fm username> <period>`\ncommands can be: `{}`\nperiod can be: `{}`\n(`period` and `username` are optional)".format(
            PREFIX, " | ".join(self.commands), " | ".join(self.intervals)
        )
        return response

    def validate(self, command: str, username: str, period: str) -> tuple[str, str, str]:

        username = quote_plus(username)

        return command, username, period
    
    async def on_message(self, message: disnake.Message):

        period = None

        if message.author == self.user:
            return

        words = message.content.split(" ")

        if PREFIX + "++" in message.content or PREFIX + " ++" in message.content:
            await message.channel.send("OwO wot's dis? thanx for kawmas >w<")
            return

        if words[0] != PREFIX:
            return


        self.log.request_classic(message.content, message.author, {})

        if len(words) == 1 or words[1] == "help":
            await message.channel.send(self.help_msg())
            return

        if len(words) >= 3:
            command, username = words[1:3]
            if username in self.intervals:
                period = username
                username, _ = message.author.name
        elif len(words) == 2:
            command = words[1]
            try:
                username = message.author.name
            except AttributeError:
                await message.channel.send(self.error_msg())
                return
        else:
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
                await message.channel.send(self.error_msg())
                return

        if command == "albums":
            re_type, response = await self.service.top_list(username, period, thing="albums")
        elif command == "artists":
            re_type, response = await self.service.top_list(username, period, thing="artists")
        elif command == "tracks":
            re_type, response = await self.service.top_list(username, period, thing="tracks")
        elif command == "collage":
            re_type, response, description = await self.service.top_collage(username, period)
        elif re.match("^[0-9]x[0-9]$", command):
            re_type, response, description = await self.service.top_collage(username, period, dims=command)
        else:
            await message.channel.send(self.error_msg())
            return

        if re_type == BotResponseCode.ERROR or re_type == BotResponseCode.TEXT:
            await message.channel.send(response)
        elif re_type == BotResponseCode.IMAGE:
            await message.channel.send(description)
            await message.channel.send(file=disnake.File(fp=response, filename="image.png"))