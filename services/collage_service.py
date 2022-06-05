import re
from io import BytesIO
from typing import List
from urllib.parse import quote_plus

import disnake
import grequests

from services.log_service import LogService
from services.log_service import BotResponseCode

from params.env_vars import FM_API_KEY
from image_processing import ImageProcessor


from utils.utils import duration_helper, get_meta, generate_top_message
from disnake.ext.commands import Bot

class CollageService():
    def __init__(self, logger: LogService):

        self.query_tracks = "https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={}&api_key={}&format=json&period={}&limit={}"
        self.query_albums = "https://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user={}&api_key={}&format=json&period={}&limit={}"
        self.query_artists = "https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={}&api_key={}&format=json&period={}&limit={}"

        self.imageProcessor = ImageProcessor()
        self.log = logger

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
            return BotResponseCode.ERROR, response

        if len(top_albums) == 0:
            response = "no albums found for user {} :pensive:".format(username)
            return BotResponseCode.ERROR, response

        response = generate_top_message(username, thing, period)+("\n".join(top_albums))
        return BotResponseCode.TEXT, response

    async def top_collage(
        self, username: str, period: str, dims: str = "3x3"
    ) -> tuple[BotResponseCode, str, None] or tuple[BotResponseCode, BytesIO, str]:

        by_x, by_y = [int(x) for x in dims.split("x")]

        rqs = [grequests.get(self.query_albums.format(username, FM_API_KEY, period, by_x * by_y))]
        responses = grequests.map(rqs)
        res = responses[0].json()

        try:
            top_albums = [get_meta(album) for album in res["topalbums"]["album"]]
            if len(top_albums) != len(res["topalbums"]["album"]):
                response = "huh i couldn't grab all the images i needed"
                return BotResponseCode.ERROR, response, None

        except:
            response = "no albums found for user {} :pensive:".format(username)
            return BotResponseCode.ERROR, response, None

        if len(top_albums) == 0:
            response = "no albums found for user {} :pensive:".format(username)
            return BotResponseCode.ERROR, response, None

        if by_x * by_y > len(top_albums):
            response = "you don't have enough albums in that period for a {}x{} collage, bucko".format(by_x, by_y)
            return BotResponseCode.ERROR, response, None

        rqs = (grequests.get(album["cover_url"]) for album in top_albums)
        responses = grequests.map(rqs)

        full_data = list(zip(responses, map(lambda a: a["info"], top_albums)))

        image_binary = self.imageProcessor.generate_collage_binary(full_data, by_x, by_y)

        description = generate_top_message(username, "albums", period)

        return BotResponseCode.IMAGE, image_binary, description
