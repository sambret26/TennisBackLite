from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from application.services import discord_service
from config import Config
from discord import Intents
from discord.ext import commands
from batchs import batchs_launcher as launcher
from infrastructure.logger.logger import log, BOT

scheduler = AsyncIOScheduler()

tz = timezone(Config.TIME_ZONE)

DISCORD_GUILD_ID = int(Config.DISCORD_GUILD_ID)

intent = Intents(messages=True, members=True, guilds=True, reactions=True, message_content=True)
bot = commands.Bot(command_prefix='$', description='Tennis 2026', intents=intent)

@bot.command()
async def check(ctx):
    await discord_service.check(ctx)

@bot.command()
async def nb(ctx):
    await discord_service.nb(bot, ctx)

@bot.command()
async def info(ctx, name = None):
    await discord_service.info(ctx, name)

@bot.command()
async def infos(ctx, name = None):
    await discord_service.info(ctx, name)

@bot.command()
async def pgw(ctx):
    await discord_service.pgw(bot)

@bot.command()
async def excel(ctx):
    await discord_service.excel(ctx)

@bot.command()
async def auth(ctx, value: int = 0):
    await discord_service.auth(ctx, value)

@bot.command()
async def cmd(ctx):
    await discord_service.cmd(ctx)

@bot.command()
async def clear(ctx, nombre: int = 100):
    await discord_service.clear(ctx, nombre)

@bot.event
async def on_ready():
    log.info(BOT, "Connected !")
    scheduler.add_job(launcher.pgw, CronTrigger(hour=8, minute=58, second=10, timezone=tz), args=[bot])
    scheduler.add_job(launcher.registrations, CronTrigger(second=20, timezone=tz))
    scheduler.add_job(launcher.call_ups, CronTrigger(second=40, timezone=tz))
    scheduler.add_job(launcher.send_notif_loop, CronTrigger(second=0, timezone=tz), args=[bot])
    scheduler.add_job(launcher.update_matches, CronTrigger(hour=2, minute=0, timezone=tz))
    scheduler.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.guild.id != DISCORD_GUILD_ID:
        return
    if message.attachments:
        await discordBusiness.importFile(message)
    await bot.process_commands(message)

def main():
    bot.run(Config.DISCORD_TOKEN)