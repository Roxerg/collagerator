import logging
from logging.handlers import RotatingFileHandler

import disnake
from disnake.ext.commands import Context
from disnake import ApplicationCommandInteraction

from enum import Enum

from disnake import Message


logging.basicConfig(datefmt="%H:%M:%S")

class BotResponseCode(Enum):
    ERROR = -1
    TEXT = 0
    IMAGE = 1


class LogService:
    def __init__(self):
        requests_filehandler = RotatingFileHandler("requests.log", mode="a", backupCount=2, maxBytes=2 * 1024 * 1024)
        errors_filehandler = RotatingFileHandler("errors.log", mode="a", backupCount=2, maxBytes=2 * 1024 * 1024)

        requests_formatter = logging.Formatter(
            "%(asctime)s | %(message)s %(guild)s %(username)s | %(command)s %(period)s %(dimensions)s %(response_code)s %(response)s %(listof)s %(count)s"
        )
        errors_formatter = logging.Formatter("%(asctime)s | %(command)s %(message)s | %(response)s")

        requests_filehandler.setFormatter(requests_formatter)
        errors_filehandler.setFormatter(errors_formatter)

        requests_logger = logging.getLogger("Collagerator_Requests")
        errors_logger = logging.getLogger("Collagerator_Errors")

        requests_level = logging.INFO
        errors_level = logging.ERROR

        requests_logger.setLevel(requests_level)
        requests_logger.addHandler(requests_filehandler)

        errors_logger.setLevel(errors_level)
        errors_logger.addHandler(errors_filehandler)

        self.requests_logger = requests_logger
        self.errors_logger = errors_logger

    def build_extras(
        self,
        command: str = "",
        username: str = "",
        dimensions: str = "",
        period: str = "",
        response_code: str = "",
        response: str = "",
        guild: str = "",
        count: str = "",
        listof: str = "",
    ) -> dict[str, str]:
        return {
            "command": command,
            "username": f"| USER:{username}",
            "dimensions": dimensions,
            "period": period,
            "response_code": response_code,
            "response": response,
            "guild": f"| GUILD:{guild}",
            "count": count,
            "listof": listof,
        }

    def add_command_params(self, extra_params: dict[str, str], extras):

        if "dimensions" in extras:
            extra_params["dimensions"] = extras["dimensions"]
        if "period" in extras:
            extra_params["period"] = extras["period"]

        return extra_params
    def request_slash(self, ctx: Context, command: str, username: str, extras: dict[str, str]):

        extra_params = self.build_extras(command=command, username=username, guild=ctx.author.guild)

        extra_params = self.add_command_params(extra_params, extras)

        self.requests_logger.info("REQ SLASH", extra=extra_params)

    def request_slash(self, inter: ApplicationCommandInteraction, command: str, username: str, extras: dict[str, str] ):
        extra_params = self.build_extras(command=command, username=username, guild=inter.guild)

        extra_params = self.add_command_params(extra_params, extras)

        self.requests_logger.info("REQ SLASH", extra=extra_params)


    def request_prefix(self, ctx: Context, command: str, username: str, extras: str):
        
        extra_params = self.build_extras(
            command=command,
            username=username,
        )

        extra_params = self.add_command_params(extra_params, extras)

        self.requests_logger.info(
            "REQ CLASSIC",
            extra=extra_params,
        )

        pass


    def request_classic(self, command: str, username: str, extras: str):

        extra_params = self.build_extras(
            command=command,
            username=username,
        )

        extra_params = self.add_command_params(extra_params, extras)

        self.requests_logger.info(
            "REQ CLASSIC",
            extra=extra_params,
        )

    def response(self, command: str, username: str, statuscode: BotResponseCode, response: str):
        self.requests_logger.info(
            "RES",
            extra=self.build_extras(
                command=command,
                username=username,
                response_code="SUCCESS" if statuscode != BotResponseCode.ERROR else "FAIL",
            ),
        )
        if statuscode == BotResponseCode.ERROR:
            self.errors_logger.error("FAIL MESSAGE", extra=self.build_extras(response=response, command=command))

    def error(self, command, extra):
        self.errors_logger.error()

    def misc(self, message: Message):
        self.requests_logger.info(message)
