import logging
from logging.handlers import RotatingFileHandler
import discord
from client import BotResponseCode

logging.basicConfig(datefmt="%H:%M:%S")


class LogService:
    def __init__(self):
        requests_filehandler = RotatingFileHandler(
            "requests.log", mode="a", backupCount=2, maxBytes=2 * 1024 * 1024
        )
        errors_filehandler = RotatingFileHandler(
            "errors.log", mode="a", backupCount=2, maxBytes=2 * 1024 * 1024
        )

        requests_formatter = logging.Formatter(
            "%(asctime)s | %(message)s %(guild)s %(username)s | %(command)s %(period)s %(dimensions)s %(response_code)s %(response)s %(listof)s %(count)s"
        )
        errors_formatter = logging.Formatter("%(asctime)s | %(message)s | %(response)s")

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
        command: str="",
        username: str="",
        dimensions: str="",
        period: str="",
        response_code: str="",
        response: str="",
        guild: str="",
        count: str="",
        listof: str="",
    )-> dict[str, str]:
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

    def request_slash(self, ctx: discord.ext.commands.Context, command: str, username: str, extras: dict[str, str]):

        extra_params = self.build_extras(
            command=command, username=username, guild=ctx.author.guild
        )

        extra_params = self.add_command_params(extra_params, extras)

        self.requests_logger.info("REQ SLASH", extra=extra_params)

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
                response_code="SUCCESS" if statuscode == 1 else "FAIL",
            ),
        )
        if statuscode != 1:
            self.errors_logger.error(
                "FAIL MESSAGE", extra=self.build_extras(response=response)
            )

    def error(self, command, extra):
        self.errors_logger.error()

    def misc(self, message: discord.Message):
        self.requests_logger.info(message)
