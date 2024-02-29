import contextlib
import logging
from datetime import datetime

import discord
from discord.ext import commands

from RoboBor.robobor import RoboBor

log = logging.getLogger(__name__)


class Server(commands.Cog):
    EMOJI = "🔧"

    def __init__(self, bot):
        self.bot: RoboBor = bot

    async def edit_afk_nick(
        self, author: discord.Member, reason: str = "AFK", mode: str = "edit"
    ):
        author_name = author.display_name
        if mode.lower() == "check":
            if author_name.startswith("[AFK]"):
                with contextlib.suppress(discord.Forbidden, discord.HTTPException):
                    await author.edit(nick=author.name, reason=reason)
                    return
        else:
            with contextlib.suppress(discord.Forbidden, discord.HTTPException):
                if not author_name.startswith("[AFK]"):
                    await author.edit(
                        nick=f"[AFK] {author_name}", reason=f"AFK cmd: {reason}"
                    )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        guild = message.guild
        author = message.author
        channel = message.channel
        mentions = [member.id for member in message.mentions]

        if not guild or (author.bot or author == self.bot.user):
            return

        data: dict = await self.bot.redis.hgetall(f"afk:{guild.id}")
        if not data:
            return

        afk_user_id = int(list(data.keys())[0])

        if afk_user_id == author.id:
            await self.bot.redis.hdel(f"afk:{guild.id}", str(author.id))
            await self.edit_afk_nick(author, reason="AFK: Reset.", mode="check")
            return await channel.send(
                f"{author.mention}, welcome back! I have removed your AFK status.",
                delete_after=5,
            )
        elif not mentions:
            return
        else:
            if afk_user_id in mentions:
                afk_data = data.get(str(afk_user_id))
                afk_data = afk_data.split("$")
                return await message.reply(
                    f"That user is currently AFK: {afk_data[0]} - {afk_data[1]}",
                    delete_after=10,
                )

    @commands.cooldown(1, 10.5, commands.BucketType.user)
    @commands.hybrid_command()
    async def afk(self, ctx: commands.Context, *, reason: str = "AFK"):
        """
        Adds a AFK status of yours with an optional reason.
        When someone pings you they will be notified of your AFK status.

        Example:
        `r!afk going out.`
        """
        send_msg = ctx.send
        if ctx.interaction:
            await ctx.interaction.response.defer()
            send_msg = ctx.interaction.followup.send
        current_time = discord.utils.format_dt(datetime.now(), "R")
        clean_reason = reason.replace("$", "dollar")
        await self.edit_afk_nick(ctx.author, reason=f"AFK: {reason}")
        await self.bot.redis.hset(
            f"afk:{ctx.guild.id}", ctx.author.id, f"{clean_reason}${current_time}"
        )
        await send_msg(
            f"{ctx.author.mention}, you are now AFK: {reason} - {current_time}"
        )


async def setup(bot: RoboBor):
    await bot.add_cog(Server(bot), guild=discord.Object(id=990593914861916230))
