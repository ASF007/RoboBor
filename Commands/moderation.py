import datetime
import logging
import time
from typing import Any, Callable, Optional, Union

import humanfriendly
from discord import *
from discord.ext import commands

from RoboBor.robobor import RoboBor
from Utils import utils as _utils
from Views.confirm_view import ConfirmView

log = logging.getLogger(__name__)

"""
required info for logs.

data = {
    "type": ctx.command.name,
    "staff": ctx.author.id, 
    "reason": reason, 
    "note": "test by", 
    "created_at": int(datetime.now().timestamp())
    }
"""


class Moderation(commands.Cog):
    EMOJI = "⚠"

    def __init__(self, bot):
        self.bot: RoboBor = bot

    async def mod_check(self, ctx: commands.Context, t: Member):
        if (
            t.guild_permissions in ("manage_messages", "manage_server", "administrator")
            or (t.top_role >= ctx.author.top_role)
            or (ctx.guild.me.top_role <= t.top_role)
            or (ctx.author.id in [t.id, ctx.guild.me.id])
        ):
            return await ctx.send(
                f"**{ctx.author.name}**, I can't {ctx.command.name} this member!"
            )

    async def timeout_check(self, ctx: commands.Context, time: int):
        if time > 2419200:
            return await ctx.send(
                f"**{ctx.author.name}**, timeouts can't be longer than 28 days!"
            )
        elif time in (1, 2):
            return await ctx.send(f"**{ctx.author.name}**, that's a little too short!")

    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.cooldown(3, 6.5, commands.BucketType.member)
    @commands.command(aliases=["kicc", "boot"])
    async def kick(
        self,
        ctx: commands.Context,
        members: commands.Greedy[Member],
        *,
        reason: str = "Not given.",
    ):
        """
        Kicks a member. No fuss. (requires kick members permission)
        Extra: Kick reason is DM'd to the member.

        Example:
        `r!kick @furry_master67 Furry's are not permitted in a non furry channel.`
        `r!kick 921022384734093372 80528701850124288 6868686886868868  pretending to be a non furry.`
        """
        if not members:
            return await ctx.send("At least provide one valid member.")
        await _utils.mass_kick(ctx, members, reason=reason)
        # data = {
        #     "type": ctx.command.name,
        #     "action": "bulk kick" if len(members) > 1 else "kick",
        #     "staff": ctx.author.id,
        #     "reason": reason,
        #     "note": f"",
        #     "created_at": int(time.time()),
        # }
        # await self.bot.log_utils.send_log(ctx, member, data)

    @commands.has_guild_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @commands.cooldown(5, 10, commands.BucketType.member)
    @commands.command(
        aliases=[
            "time",
            "to",
            "mute",
            "1984",
            "silence",
            "shutup",
            "shush",
            "shut",
            "stfu",
        ]
    )
    async def timeout(
        self,
        ctx: commands.Context,
        member: Member,
        duration: str,
        *,
        reason: str = "Not given.",
    ):
        """
        Times out a member and logs it. (requires timeout members permission)

        Example:
        `r!timeout @annoyingperson1 30m spamming (30 minute timeout)`
        `r!timeout @annoyingperson2 2.5h being dumb (2.5 hour timeout)`
        """
        if await self.mod_check(ctx, member):
            return
        try:
            duration = humanfriendly.parse_timespan(duration)
        except humanfriendly.InvalidTimespan or int(duration[0]) < 0:
            duration = 600.0

        await self.timeout_check(ctx, duration)

        timeout_duration = utils.utcnow() + datetime.timedelta(seconds=duration)
        await member.timeout(timeout_duration, reason=reason)

        total_timeout_period = _utils.td_format(duration)

        await ctx.send(
            f"{self.bot.emoji['confirm']} **{member.name} has been timed out!** ({total_timeout_period})\n"
            f"Ends: {utils.format_dt(timeout_duration, 'R')}"
        )

        data = {
            "type": ctx.command.name,
            "action": "timeout",
            "staff": ctx.author.id,
            "reason": reason,
            "note": f"{total_timeout_period} timeout",
            "created_at": int(time.time()),
        }
        await self.bot.log_utils.send_log(ctx, member, data)

    @commands.has_guild_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @commands.cooldown(3, 6.5, commands.BucketType.member)
    @commands.command(aliases=["untime", "uto", "unmute"])
    async def untimeout(
        self, ctx: commands.Context, member: Member, *, reason: str = "Not given."
    ):
        """
        Un-timeout a user.

        Example:
        `r!untimeout @someguy we cool now`
        """
        if await self.mod_check(ctx, member):
            return
        if not member.is_timed_out():
            return await ctx.send(
                f"**{ctx.author.name}**, that member isn't timed out!"
            )

        await member.timeout(None, reason=reason)

        await ctx.send(
            f"{self.bot.emoji['confirm']} **{member.name} has been un-timed out!**"
        )

        data = {
            "type": ctx.command.name,
            "action": "un-timeout",
            "staff": ctx.author.id,
            "reason": reason,
            "note": f"manual un-timeout",
            "created_at": int(time.time()),
        }
        await self.bot.log_utils.send_log(ctx, member, data, True)

    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(5, 6.5, commands.BucketType.member)
    @commands.group(aliases=["clean", "c", "p"], invoke_without_command=True)
    async def purge(
        self,
        ctx: commands.Context,
        limit: int,
        channel: Optional[Union[TextChannel, Thread, VoiceChannel]] = None,
    ):
        """
        Deletes messages by matching the given optional conditions.
        Usage: r!purge <limit> <channel=None>

        If you simply want to delete the messages from a specific/current channel, then pass in the args of this command.
        Otherwise make use of the subcommands which offer extra purging options by going through the buttons below.

        Example:
        `!purge 2 #general`
        `!purge 25`
        """
        if limit >= 150:
            return await ctx.send(
                f"Dear {ctx.author.mention}, You can only delete `150` messages in a try. Don't be greedy.",
                delete_after=7,
            )
        if channel is None:
            channel = ctx.channel
        await ctx.message.delete()
        purged = await channel.purge(
            limit=limit, reason=f"{ctx.author}: Used Purge command."
        )
        await ctx.send(
            f"{self.bot.emoji['confirm']} Deleted `{len(purged)}` message(s) from {channel.mention}",
            delete_after=7,
        )

    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(1, 6.5, commands.BucketType.member)
    @purge.command(aliases=["u"])
    async def user(self, ctx: commands.Context, member: Member, limit: int):
        """
        Deletes the messages for the given user.

        Example:
        `!purge user @ASF 5`
        `!p u 00000000007 30`
        """
        await self.delete_messages(
            ctx, limit, lambda x: x.author == member, f" from *{member}*."
        )

    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(1, 6.5, commands.BucketType.member)
    @purge.command(aliases=["b", "bots"])
    async def bot(
        self,
        ctx: commands.Context,
        member: Member,
        prefix: Optional[str] = None,
        limit: int = 25,
    ):
        """
        Deletes the messages for the given bot or with the prefixed messages.

        Note: For this command the amount defaults to 25 if not supplied any.

        Example:
        `!purge bot @RoboBor ! 5`
        `!p b 91111111111111 30`
        """

        def check(m):
            return (m.webhook_id is None and m.author.bot and m.author == member) or (
                prefix and m.content.startswith(prefix)
            )

        await self.delete_messages(ctx, limit, check, f" from the bot user *{member}*.")

    async def delete_messages(
        self,
        ctx: commands.Context,
        amount: int,
        check: Callable[[Message], Any],
        extra: Optional[str] = "",
    ):
        if amount >= 150:
            return await ctx.send(
                f"Dear {ctx.author.mention}, You can only delete `150` messages in a try. Don't be greedy.",
                delete_after=7,
            )
        await ctx.message.delete()
        purged = await ctx.channel.purge(
            limit=amount, check=check, reason=f"{ctx.author}: Used Purge command."
        )
        msg_to_send = f"{self.bot.emoji['confirm']} Deleted `{len(purged)}` message(s)"
        if extra:
            msg_to_send += extra
        await ctx.send(msg_to_send, delete_after=7)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
