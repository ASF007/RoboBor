import asyncio
from typing import Union
from urllib.error import ContentTooShortError

import discord
from discord import Member, User
from discord.ext.commands import Context, Greedy

async def mass_kick(
    ctx: Context, members: Greedy[Member], *, reason: str = "Not given."
):
    sucess = 0
    fails = 0
    failure_reason = ""
    main_msg = await ctx.send(content=f"Filtering duplicate members..")
    await asyncio.sleep(1)
    if len(members) == 0:
        await main_msg.edit(content="Please provide proper members for me to kick.")
        return
    await main_msg.edit(
        content=f"Filtered duplicates.. now proceeding to kick {len(members)}"
    )
    await asyncio.sleep(2)
    for member in members:
        if member is None or not (member in ctx.guild.members):
            await main_msg.edit(content="Checking for users not present..")
            await asyncio.sleep(2)
            failure_reason += f"{member}: is not in the server.\n"
            fails += 1
        try:
            await ctx.guild.kick(member, reason=reason)
            sucess += 1
            await main_msg.edit(
                content=f"`{sucess}/{len(members)}` members kicked so far."
            )
            await asyncio.sleep(2)
        except discord.Forbidden:
            failure_reason += f"{member} ({member.id}) : I do not have the required permissions to kick that user/ my role may not be above theirs.\n"
            await main_msg.edit(content=f"Fail encountered....")
            await asyncio.sleep(2)
            fails += 1
        except discord.HTTPException as e:
            failure_reason += f"{member} ({member.id}) : {e}\n"
            await main_msg.edit(content=f"Fail encountered....")
            await asyncio.sleep(2)
            fails += 1

        except Exception as e:
            failure_reason += f"{member}: {e}\n"
            fails += 1

    await main_msg.edit(content="*Mass kicking completed.*")
    msg = (
        f"Sucessfully kicked `{sucess}/{len(members)}` members."
        if sucess != 0
        else "Mass kicking failed... please refer below:"
    )
    await ctx.send(msg)
    if failure_reason:
        await ctx.send(
            f"Failed to kick **{fails}** members.\n```\n{failure_reason}\n```"
        )


def td_format(td_object):
    seconds = int(td_object)
    periods = [
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 30),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = "s" if period_value > 1 else ""
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)


def beautiful_time(t: float) -> str:
    t = int(t)
    min, sec = divmod(t, 60)
    hour, min = divmod(min, 60)
    day, hour = divmod(hour, 60)

    days = str(day) + " days" if day else ""
    hours = str(hour) + " hours" if hour else ""
    mins = str(min) + " minutes" if min else ""
    secs = str(sec) + " seconds" if sec else ""
    return f"{days} {hours} {mins} {secs}"
