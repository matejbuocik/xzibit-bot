#!/usr/bin/python3

import asyncio
from datetime import datetime
import logging
import os
import random
import re
import time

import aiofiles
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands

from assets.nameday import nameday_from_date, nameday_from_name
from assets.get_wiki import get_wiki
from assets.get_quote import get_quote


# --- Configuration ---
load_dotenv()

intents = nextcord.Intents.default()
intents.message_content = True

description = "Yo wassup this is xzibit"

bot = commands.Bot(
    command_prefix="$",
    intents=intents,
    description=description,
    activity=nextcord.Game(name="pimpin'"))


# --- Logging ---
logger = logging.getLogger("nextcord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="nextcord.log", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)


LOG = "messages.log"
@bot.listen()
async def on_message(message: nextcord.Message):
    async with aiofiles.open(LOG, mode="a") as file:
        time_str = time.strftime("%Y-%m-%d|%H:%M:%S")
        if message.author != bot.user:
            await file.write(
                f"{time_str}|{message.author.name}|{message.channel.name}|{message.content}\n")


# --- Events and commands ---
@bot.event
async def on_ready() -> None:
    """Print bot details when ready"""
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.command()
async def hi(ctx: commands.Context) -> None:
    """Just a simple hi"""
    await ctx.reply('Hi!')


@bot.command(aliases=["pingpong"])
async def ping(ctx: commands.Context) -> None:
    """Check bot responsiveness and get the latency"""
    await ctx.send(f"🏓 **PONG!** Latency is ~{bot.latency:.2f}ms")


@bot.command(aliases=["povedz"])
async def say(ctx: commands.Context, *, arg: str) -> None:
    """Make the bot say something"""
    # the star before arg is so that arg with spaces
    # does not have to be in quotes
    await ctx.send(arg)


@bot.command(aliases=["kto_som", "who am i", "who"])
async def whoami(ctx: commands.Context) -> None:
    """Respond with a name of the author"""
    try:
        await ctx.send(ctx.author)
    except Exception:
        await ctx.send("Command not found")


@bot.command()
async def quote(ctx: commands.Context) -> None:
    """Send a random quote"""
    await ctx.trigger_typing()
    text = await get_quote()
    await ctx.send(text)


@bot.command(usage="`$wiky <query>`")
async def wiki(ctx: commands.Context, *, query: str) -> None:
    """Query wikipedia and send a short answer"""
    await ctx.trigger_typing()
    result = await get_wiki(query)
    await ctx.send(result)


@bot.command(usage="`$nameday <date>` or `$nameday <name>`", aliases=["meniny"])
async def nameday(ctx: 'commands.Context', *, arg: str = "") -> None:
    """Get a name's nameday or vice versa"""
    if not arg:
        await ctx.send(await nameday_from_date("assets/meniny.csv", datetime.today().day, datetime.today().month))

    else:
        input_nums = [int(n) for n in re.findall(r'[0-9]+', arg)]

        if len(input_nums) < 2:
            await ctx.send(await nameday_from_name("assets/meniny.csv", arg))
        else:
            await ctx.send(await nameday_from_date("assets/meniny.csv", input_nums[0], input_nums[1]))


@bot.command()
async def guess(ctx: commands.Context) -> None:
    """Guess a number game"""
    await ctx.send("Guess a number between 1 and 100.")

    def check(m: nextcord.Message) -> bool:
        return m.author == ctx.author and m.content.isdigit() and m.channel == ctx.channel

    answer = random.randint(1, 100)

    try:
        guess = await bot.wait_for("message", check=check, timeout=5.0)
    except asyncio.TimeoutError:
        await ctx.send(f"You took too long. It was {answer}.")

    if int(guess.content) == answer:
        await ctx.send("You are right!")
    else:
        await ctx.send(f"Oops. It is actually {answer}.")


@bot.command()
async def pimp(ctx: commands.Context) -> None:
    """Wait for a reaction"""
    message_sent = await ctx.send("Give me some 🚗 to pimp")

    def check(reaction: nextcord.Reaction, user: nextcord.User) -> bool:
        return reaction.message == message_sent and user == ctx.author and reaction.emoji == "🚗"

    try:
        await bot.wait_for("reaction_add", check=check, timeout=10.0)
    except asyncio.TimeoutError:
        await ctx.send("Yo man too late")
    else:
        await ctx.send("pimpin' time")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
