# imports
import logging
import os

import discord

from bot_base import BotBase
from dotenv import load_dotenv

from Utils import data_utils


# funtions
load_dotenv() # loads our .env file
logging.basicConfig(level=logging.INFO) # configuring the logging module, pretty important and useful

# constants
MONGO_URL = os.getenv("MONGO_URL") # our mongoDB url
TOKEN = os.getenv("MAIN_TOKEN") # the token our bot will be running on

# intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


# bot object
bot = BotBase(
    command_prefix="r!",
    intents=intents,
    mongo_url=MONGO_URL,
    mongo_database_name="robor"
)

# global variables
bot.version = "1.0a"

# Events
@bot.event
async def on_ready():
    """This event fires up when our bot has logged into discord."""
    print("------")
    print(f"Logged in as: {bot.user} (ID: {bot.user.id})")
    print("------")
    

if __name__ == "__main__":
    bot.run(TOKEN, reconnect=True)