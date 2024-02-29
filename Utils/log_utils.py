from datetime import datetime
from typing import Union

import discord
from discord.ext import commands

# from RoboBor.robobor import RoboBor


class LogUtils:
    def avatar_url(self, m: Union[discord.Member, discord.User]):
        return m.avatar.url if m.avatar else m.default_avatar.url

    async def send_log(
        self,
        ctx: commands.Context,
        target: discord.Member,
        data: dict,
        color: bool = False,
    ):
        color = discord.Color.dark_red() if not color else discord.Color.brand_green()
        current_config = await ctx.bot.db.config.find({"_id": ctx.guild.id})
        if not current_config:
            return
        else:
            channel = ctx.guild.get_channel(current_config.get("log_channel"))
            if not channel:
                return
            else:
                log_id = (
                    len(
                        await ctx.bot.db.logs.find_many(
                            {"guild_id": ctx.guild.id, "target_id": target.id}
                        )
                    )
                    + 1
                )

                await ctx.bot.db.logs.upsert(
                    {
                        "guild_id": ctx.guild.id,
                        "target_id": target.id,
                        "log_id": log_id,
                    },
                    data,
                )
                webhooks = await channel.webhooks()
                bot = ctx.guild.me
                for webhook in webhooks:
                    if webhook.user == bot and webhook.name == f"{bot.name} Logging":
                        break
                else:
                    try:
                        webhook = await channel.create_webhook(
                            name=f"{bot.name} Logging", avatar=await bot.avatar.read()
                        )
                    except (discord.HTTPException, discord.Forbidden):
                        return await ctx.send(
                            f"Failed log this action to {channel.mention}, due to being able to create a webhook."
                        )

                embed = discord.Embed(title=data["note"], color=color)
                embed.description = (
                    f"{data['reason']} ({data['action']} by <@{data['staff']}>)"
                )
                embed.timestamp = datetime.fromtimestamp(data["created_at"])
                embed.set_author(
                    name=f"{target} has been {data['type']}",
                    icon_url=self.avatar_url(target),
                )
                embed.set_footer(text=target.id)
                await webhook.send(embed=embed)
