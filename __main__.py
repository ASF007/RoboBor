# imports
import asyncio
import logging
import os

import discord
from dotenv import load_dotenv

from RoboBor.robobor import RoboBor

# funtions
load_dotenv()  # loads our .env file
logging.basicConfig(
    level=logging.INFO
)  # configuring the logging module, pretty important and useful

# constants
TOKEN = os.getenv("MAIN_TOKEN")  # the token our bot will be running on


if __name__ == "__main__":
    bot = RoboBor()
    bot.run(TOKEN, reconnect=True)
