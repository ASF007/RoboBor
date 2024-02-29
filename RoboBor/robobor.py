# imports
import logging
import os

import aiohttp
import aioredis
import discord
from bot_base import BotBase
from dotenv import load_dotenv

from Commands import EXTENSIONS
from Utils import data_utils, log_utils

# funtions
load_dotenv()  # loads our .env file
# logging.basicConfig(level=logging.INFO) # configuring the logging module, pretty important and useful

# logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("RoboBor.log", mode="w")
file_handler.setFormatter(
    logging.Formatter("%(levelname)s:%(filename)s:%(lineno)d:%(asctime)s:%(message)s")
)
log.addHandler(file_handler)

# constants
MONGO_URL = os.getenv("MONGO_URL")  # our mongoDB url
REDIS_URL = os.getenv("REDIS_URL")
REDIS_PORT = os.getenv("REDIS_PORT")
TOKEN = os.getenv("MAIN_TOKEN")  # the token our bot will be running on
ERROR_CHANNEL = os.getenv("ERROR_LOG_CHANNEL")
LOG_CHANNEL = os.getenv("LOG_CHANNEL")

# intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Our bot's subclass
class RoboBor(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            command_prefix="r!",
            intents=intents,
            activity=discord.Streaming(
                name="I'm RoboBor", url="https://www.twitch.tv/ninja"
            ),
            mongo_url=MONGO_URL,
            mongo_database_name="robor",
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=True, users=True, replied_user=True
            ),
        )
        self.version = "1.0a"
        self.RoboBorLogger = log
        self.log_utils = log_utils.LogUtils()

    @property 
    def embed(self, msg: str, emb_type: str = "sucess", emote: str = None):
        if emote is None:
            emote = self.emotes.get("sucess") if emb_type == "sucess" else self.emotes.get("cross")
        embed = discord.Embed(description = f"{emote} {msg}")
        embed.color = discord.Color.green() if emb_type == "sucess" else discord.Color.red()
        return embed

    async def on_ready(self) -> None:
        print(f"Logged in as: {self.user} (ID: {self.user.id})")
        print("------")
        await self.wait_until_ready()
        await self.log_channel.send("Bot rebooted!")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        elif message.author == self.user:
            return
        else:
            await self.process_commands(message)

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.redis = aioredis.from_url(
            REDIS_URL, port=REDIS_PORT, encoding="utf-8", decode_responses=True
        )
        log.info("Connected to redis..")

        self.config = await data_utils.read_file("Data/config.json")
        self.emotes = self.config.get("emojis")

        self.log_channel = await self.get_or_fetch_channel(LOG_CHANNEL)
        self.error_log_channel = await self.get_or_fetch_channel(ERROR_CHANNEL)

        print("------")
        if self.load_builtinn:
            await self.load_extension("bot_base.cogs.internal")
            log.info("Loaded internal")
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
                log.info("Loaded %s", ext)
            except Exception as e:
                log.critical("Could not load %s because: %s", ext, e)
        print("------")

    async def close(self) -> None:
        log.info("Shudown initialized... cleaning up.")
        await self.redis.close()
        await self.session.close()
        await super().close()
        log.info("Clean shudown complete.")
