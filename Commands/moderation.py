import logging

from discord.ext import commands

log = logging.getLogger(__name__)


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Ready")

    

    


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
