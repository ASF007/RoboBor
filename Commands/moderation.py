import logging
from typing import Any, Callable, Optional, Union

from discord import *
from discord.ext import commands

log = logging.getLogger(__name__)


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Ready")


    @commands.has_guild_permissions(manage_messages = True)
    @commands.bot_has_permissions(manage_messages = True)
    @commands.cooldown(1, 6.5, commands.BucketType.member)
    @commands.group(aliases=["clean", "c", "p"], invoke_without_command = True)
    async def purge(self, ctx: commands.Context, limit: int, channel: Optional[Union[TextChannel, Thread, VoiceChannel]] = None):
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
            return await ctx.send(f"Dear {ctx.author.mention}, You can only delete `150` messages in a try. Don't be greedy.", delete_after=7)
        if channel is None:
            channel = ctx.channel
        await ctx.message.delete()
        purged = await channel.purge(limit=limit, reason=f"{ctx.author}: Used Purge command.")
        await ctx.send(f"Deleted `{len(purged)}` message(s) from {channel.mention}", delete_after=7)


    @commands.has_guild_permissions(manage_messages = True)
    @commands.bot_has_permissions(manage_messages = True)
    @commands.cooldown(1, 6.5, commands.BucketType.member)
    @purge.command(aliases = ["u"])
    async def user(self, ctx: commands.Context, member: Member, limit: int):
        """
        Deletes the messages for the given user.

        Example:
        `!purge user @ASF 5`
        `!p u 00000000007 30`
        """
        await self.delete_messages(ctx, limit, lambda x: x.author == member, f" from *{member}*.")

    @commands.has_guild_permissions(manage_messages = True)
    @commands.bot_has_permissions(manage_messages = True)
    @commands.cooldown(1, 6.5, commands.BucketType.member)
    @purge.command(aliases = ["b", "bots"])
    async def bot(self, ctx: commands.Context, member: Member, prefix: Optional[str] = None, limit: int = 25):
        """
        Deletes the messages for the given bot or with the prefixed messages.

        Note: For this command the amount defaults to 25 if not supplied any.

        Example:
        `!purge bot @RoboBor ! 5`
        `!p b 91111111111111 30`
        """
        def check(m):
            return (m.webhook_id is None and m.author.bot and m.author == member) or (prefix and m.content.startswith(prefix))
        await self.delete_messages(ctx, limit, check, f" from the bot user *{member}*.")

    async def delete_messages(
        self,
        ctx: commands.Context,
        amount: int,
        check: Callable[[Message], Any],
        extra: Optional[str] = "",
        ):
        if amount >= 150:
            return await ctx.send(f"Dear {ctx.author.mention}, You can only delete `150` messages in a try. Don't be greedy.", delete_after=7)
        await ctx.message.delete()
        purged = await ctx.channel.purge(limit=amount, check=check, reason=f"{ctx.author}: Used Purge command.")
        msg_to_send = f"Deleted `{len(purged)}` message(s)"
        if extra:
            msg_to_send += extra
        await ctx.send(msg_to_send, delete_after=7)
    

    


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
