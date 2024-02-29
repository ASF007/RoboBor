# imports
import logging
from typing import List, Mapping, Optional

import discord
from bot_base.paginators.discord_paginator import discordPaginator
from discord.ext import commands
from discord.ext.commands import Cog, Command, Group

from RoboBor.robobor import RoboBor

# logger
log = logging.getLogger(__name__)

# variable
URLS = (
    ("Commands", "https://gist.github.com/ASF007/3bca1d8d4a9f9b136261e02a836deb24"),
    ("Changelog", "https://gist.github.com/ASF007/d5299239251a1d128641eebe1a068a07"),
    ("Support", "https://discord.gg/BwxC4JhT52"),
    (
        "Add Me!",
        discord.utils.oauth_url(
            990599121033388062,
            permissions=discord.Permissions(545394125942),
            scopes=("bot", "applications.commands"),
        ),
    ),
)
IGNORED = ("Help", "Internal", "Backend", "ErrorHandler")

# our subclass of HelpCommand
class RoboBorHelp(commands.HelpCommand):
    """Custom Help Command to resemble the one used by RoboTop."""

    def __init__(self, urls: tuple = None, ignored_categories: tuple = None):
        super().__init__(
            command_attrs={
                "cooldown": commands.CooldownMapping.from_cooldown(
                    1, 5.0, commands.BucketType.member
                ),
                "help": "Get help on various commands and categories.",
                "aliases": ["h"],
            }
        )
        self.urls = urls
        self.ignored = ignored_categories

    def help_view(self):
        """Returns the view with url style buttons."""
        if self.urls:
            view = discord.ui.View()
            for i in self.urls:
                view.add_item(discord.ui.Button(label=i[0], url=i[1]))
            return view
        else:
            return None

    def command_not_found(self, string: str) -> str:
        return f"**{self.context.author.name}**, that command doesn't exist!"

    def get_command_signature(self, command: Command) -> str:
        return (
            f"{self.context.clean_prefix}{command.qualified_name} {command.signature}"
        )

    def fmt_help(self, cmd: Command) -> str:
        """Wacky method which saves me some time & effort."""
        try:
            command_help = cmd.help.splitlines()
            command_help.pop(0)
            formatted_help_str = "{}\n{}\n\n".format(
                command_help[1], "\n".join(command_help[2:])
            )
        except (IndexError, AttributeError):
            formatted_help_str = ""

        aliases = cmd.aliases
        if aliases:
            formatted_help_str += "Aliases: " + ", ".join(aliases)

        return formatted_help_str

    async def send_bot_help(
        self, mapping: Mapping[Optional[Cog], List[Command]]
    ) -> None:
        # local vars to make function more readable xD
        prefix = (
            self.context.clean_prefix
        )  # return a clean prefix if the bot was mentioned ie @robotop
        bot = self.context.bot
        icon_url = (
            bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
        )

        # Setting  up our basic embed
        embed = discord.Embed(color=discord.Color.orange())
        embed.description = (
            f"**Type `{prefix}help [command]` for information on a command.**\n\n"
        )
        embed.set_author(name="Command List", icon_url=icon_url)
        embed.set_footer(
            text=f"{bot.version or 'SuS'} ."
            f"Currently in {len(bot.guilds)} servers.\n"
            "Bot created by ASF#4658."
        )

        # Modyfing our embed to show up the commands and categories robotop style ;)
        for cog, commands in mapping.items():
            if cog is not None:  # Ignore No Category commands
                if not cog.qualified_name in self.ignored:
                    cmds = ", ".join(f"`{cmd.name}`" for cmd in commands)
                    cog_emoji = getattr(cog, "EMOJI", "❓")
                    embed.description += (
                        f"{cog_emoji} **{cog.qualified_name}** - {cmds}\n\n"
                    )
        await self.get_destination().send(embed=embed, view=self.help_view())

    async def send_cog_help(self, cog: Cog) -> None:
        # Local variables
        prefix = self.context.clean_prefix
        cog_emoji = getattr(cog, "EMOJI", "❓")

        # Embed
        embed = discord.Embed(
            title=f"{cog_emoji} {cog.qualified_name}", color=discord.Color.orange()
        )
        embed.description = ""
        embed.set_footer(
            text=f"Type {prefix}help [command] for information on a specific command."
        )

        # Robotop style Category
        for command in cog.get_commands():
            embed.description += f"**{command.name}:** {command.short_doc or 'No description available.'}\n"
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: Command) -> None:
        help_str = (
            f"**{command.qualified_name}:** {command.short_doc or 'No description available.'}\n"
            f"Usage: {self.get_command_signature(command)}\n\n"
            f"{self.fmt_help(command)}"
        )

        await self.get_destination().send(help_str)

    async def send_group_help(self, group: Group) -> None:
        subcommands = group.commands
        if len(subcommands) == 0:
            await self.send_command_help(group)
            return

        fmt_embeds = list()
        page_no = 0

        for command in subcommands:
            page_no += 1
            embed = discord.Embed(color=discord.Color.orange())
            embed.description = (
                f"**{group.qualified_name}:** {group.short_doc}\n\n"
                "__Subcommands__\n"
                f"`{self.get_command_signature(command)}`- {command.short_doc}"
            )
            embed.set_footer(text=f"Page No: {page_no}")
            fmt_embeds.append(embed)

        # formatting our paginator
        paginator = discordPaginator(1, fmt_embeds)
        await paginator.start(context=self.context)

    async def on_help_command_error(
        self, ctx: commands.Context[RoboBor], error: commands.CommandError, /
    ) -> None:
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
            # Ignore missing permission errors
            if isinstance(error, discord.HTTPException) and error.code == 50013:
                return
            else:
                await ctx.send(str(error))


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        help_cmd = RoboBorHelp(URLS, IGNORED)
        help_cmd.cog = self
        bot.help_command = help_cmd


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
