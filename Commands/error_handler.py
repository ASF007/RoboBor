# imports
import contextlib
import random
import sys
import traceback
from datetime import datetime

from discord import *
from discord.ext import commands

from RoboBor.robobor import RoboBor
from Utils.utils import td_format


class ErrorHandler(commands.Cog):
    EMOJI = "💡"

    def __init__(self, bot: RoboBor):
        self.bot: RoboBor = bot
        self.carl_mode = False
        self._response: str = random.choice(bot.config["missing_perm_responses"])
        bot.tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        error = getattr(error, "original", error)

        if hasattr(ctx.command, "on_error"):
            return

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, errors.NotFound):
            return

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(
                f"**{ctx.author.name}**, **{ctx.command.name}** is disabled."
            )

        elif isinstance(error, commands.NoPrivateMessage):
            with contextlib.suppress(Forbidden, HTTPException):
                await ctx.send("Commands are disabled in dms.")

        elif isinstance(error, commands.errors.RoleNotFound):
            await ctx.send(
                f"**{ctx.author.name}**, I couldn't find a role named `{error.argument}`!"
            )

        elif isinstance(error, commands.errors.ChannelNotFound):
            await ctx.send(f"**{ctx.author.name}**, I couldn't find that channel!")

        elif isinstance(error, Forbidden):
            await ctx.send(
                f"**{ctx.author.name}**, I do not have the right permission(s) required to execute this command."
            )

        elif isinstance(error, commands.errors.MissingPermissions):
            chance = random.randint(0, 10)
            content = self._response.format(ctx.author.name)
            if chance == 7:
                perm = (
                    "permission"
                    if len(error.missing_permissions) == 0
                    else "permissions"
                )
                content = f"You are missing `{', '.join(error.missing_permissions).replace('_', ' ')}` {perm} to run this command."
            await ctx.send(content=content)

        elif isinstance(error, commands.errors.BotMissingPermissions):
            chance = random.randint(0, 10)
            content = self._response.format(ctx.author.name)
            if chance == 7:
                perm = (
                    "permission"
                    if len(error.missing_permissions) == 0
                    else "permissions"
                )
                content = f"It seems I'm missing `{', '.join(error.missing_permissions).replace('_', ' ')}` {perm} to run this command."
            await ctx.send(content=content)

        elif isinstance(error, commands.errors.MaxConcurrencyReached):
            per = str(error.per)[11:].title()
            await ctx.send(
                f"Maximum command invocations at the same time reached, please try again later. Limit: `{error.number}`, Per: `{per}`"
            )

        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(f"**{ctx.author.name}**, I can't find this member!")

        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(f"**{ctx.author.name}**, I can't find this user!")

        elif isinstance(error, commands.BadArgument):
            await ctx.send(str(error))

        elif isinstance(error, commands.errors.BadUnionArgument):
            await ctx.send("it doesn't look like a user with that ID exists!")

        elif isinstance(error, commands.errors.NotOwner):
            pass

        elif isinstance(error, commands.MissingRequiredArgument):
            if self.carl_mode:
                missing = str(error.param.name)
                command = (
                    f"{ctx.clean_prefix}{ctx.command.name} {ctx.command.signature}"
                )
                space = " " * (
                    len(
                        [item[::-1] for item in command[::-1].split(missing[::-1], 1)][
                            ::-1
                        ][0]
                    )
                    - 1
                )
                indicator = "^" * int(len(missing) + 2)
                await ctx.send(
                    f"```yml\nSyntax: {command}\n {space}{indicator}\n {missing} "
                    f"is a required argument that is missing.\n```"
                )
            else:
                await ctx.send_help(ctx.command)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            retry_after = td_format(error.retry_after)
            await ctx.send(
                content=f"You are on a cooldown. Maybe try again after **{retry_after}**.",
            )
        else:
            await ctx.send(
                "An unexpected error has been encountered. I have reported it."
                "Join the support server for further help."
            )
            embed = Embed(
                title=f"Error in /{ctx.command.qualified_name}",
                description=f"```py\n{str(error)}\n```",
                color=Color.red(),
            )
            embed.timestamp = datetime.now()
            embed.add_field(
                name="Server",
                value=f"Name: `{ctx.guild.name}` ({ctx.guild.id})",
            )
            embed.add_field(name="Invoker", value=f"{ctx.author} ({ctx.author.id})")
            embed.add_field(name="Invoking Message", value=ctx.message.content)

            await self.bot.error_log_channel.send(embed=embed)

            print(
                "Ignoring Exception in `message` command {}".format(ctx.command),
                file=sys.stderr,
            )
            self.bot.RoboBorLogger.fatal(error)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )

    async def on_app_command_error(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        error = getattr(error, "original", error)

        if isinstance(error, app_commands.errors.MissingPermissions):
            chance = random.randint(0, 10)
            content = self._response.format(interaction.user.name)
            if chance == 7:
                perm = (
                    "permission"
                    if len(error.missing_permissions) == 0
                    else "permissions"
                )
                content = f"You are missing `{', '.join(error.missing_permissions).replace('_', ' ')}` {perm} to run this command."
            await interaction.response.send_message(content=content, ephemeral=True)

        elif isinstance(error, app_commands.errors.CommandOnCooldown):
            retry_after = td_format(error.retry_after)
            await interaction.response.send_message(
                content=f"You are on a cooldown. Maybe try again after **{retry_after}**.",
                ephemeral=True,
            )

        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            perm = (
                "permission" if len(error.missing_permissions) == 0 else "permissions"
            )
            content = f"It seems I'm missing `{', '.join(error.missing_permissions).replace('_', ' ')}` {perm} to run this command."
            await interaction.response.send_message(content=content, ephemeral=True)

        elif isinstance(error, app_commands.errors.NoPrivateMessage):
            with contextlib.suppress(Forbidden, HTTPException):
                await interaction.response.send_message("Commands are disabled in dms.")

        elif isinstance(error, app_commands.errors.MissingRole):
            await interaction.response.send_message(
                f"You are missing `{error.missing_role}` role.", ephemeral=True
            )
        elif isinstance(error, app_commands.errors.CommandNotFound):
            pass

        else:
            await interaction.response.send_message(
                "An unexpected error has been encountered. I have reported it."
                "Join the support server for further help."
            )
            embed = Embed(
                title=f"Error in /{interaction.command.qualified_name}",
                description=f"```py\n{str(error)}\n```",
                color=Color.red(),
            )
            embed.timestamp = datetime.now()
            embed.add_field(
                name="Server",
                value=f"Name: `{interaction.guild.name}` ({interaction.guild_id})",
            )
            embed.add_field(
                name="Invoker", value=f"{interaction.user} ({interaction.user.id})"
            )
            embed.add_field(name="Invoking Message", value=interaction.message.content)

            await self.bot.error_log_channel.send(embed=embed)

            print(
                "Ignoring Exception in `app` command {}".format(interaction.command),
                file=sys.stderr,
            )
            self.bot.RoboBorLogger.fatal(error)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )


async def setup(bot: RoboBor):
    await bot.add_cog(ErrorHandler(bot))
