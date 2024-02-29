# imports
from typing import Optional

import discord
from discord import *
from discord.ext import commands

from Commands import EXTENSIONS
from RoboBor.robobor import RoboBor
from Views.confirm_view import ConfirmView


class Backend(commands.Cog):
    EMOJI = "⚙"

    def __init__(self, bot: RoboBor):
        self.bot: RoboBor = bot
        self.cache = {}
        self.conf_emoji = bot.emotes["confirm"]
        self.err_emoji = bot.emotes["cancel"]

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.guild is None and not message.author.bot:
            if  self.cache and self.cache.get(message.content):
                data = self.cache.get(message.content)
            else:
                async with self.bot.session.get(
                    f"https://chatbot-api.gq/?message={message.content}"
                ) as r:
                    if r.status == 200:
                        data = await r.text()
                        self.cache[message.content] = data
                    else:
                        data = "Im out of oil 🛢 at the moment. Maybe try again later?"
            async with message.channel.typing():
                await message.channel.send(data)
                return
        else:
            return
        

    @commands.command(hidden=True, aliases=["handle"])
    @commands.is_owner()
    async def operate(
        self, ctx: commands.Context, cog: str.lower, action: str.lower = "reload"
    ):
        """Loads/reloads/unloads the given cog."""
        mode_dict = {
            "reload": self.bot.reload_extension,
            "load": self.bot.load_extension,
            "unload": self.bot.unload_extension,
        }
        try:
            await mode_dict[action](f"Commands.{cog}")
            await ctx.message.add_reaction(self.conf_emoji)
            action = action + "ed"
            self.bot.RoboBorLogger.info(f"%s %s cog.", action, cog)
        except Exception as e:
            await ctx.message.add_reaction(self.err_emoji)
            await ctx.send(e)

    @commands.command()
    @commands.is_owner()
    async def off(self, ctx: commands.Context):
        """Shutdown's the bot"""
        await ctx.send("Shutting down 👋")
        await self.bot.close()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sync(
        self,
        ctx: commands.Context,
        guild_id: Optional[int] = None,
        mode: Optional[str] = "normal",
    ):
        """
        Sync's the bot's application commands.
        """
        if mode == "*":
            view = ConfirmView(
                ctx,
                "Sync!",
                "Synced app cmds for all servers.",
                "You did not respond in time.",
            )
            view.message = await ctx.send(
                "This will **sync** the app commands **globally**.", view=view
            )
            await view.wait()
            if view.value:
                await self.bot.tree.sync()
                self.bot.RoboBorLogger.info(f"Synced app commands globally.")
                return
        else:
            guild_id = guild_id or ctx.guild.id
            await self.bot.tree.sync(guild=discord.Object(guild_id))
            await ctx.message.add_reaction(self.conf_emoji)
            self.bot.RoboBorLogger.info(f"Synced app commands for ({guild_id}).")


async def setup(bot: commands.Bot):
    await bot.add_cog(Backend(bot))
