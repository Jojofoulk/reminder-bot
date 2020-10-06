import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.ext.tasks import loop
import asyncio
from datetime import datetime, time
import os
import pytz
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Bot running")
    activity = discord.Activity(name=f'Reminding you of stuff', type=discord.ActivityType.playing)
    await bot.change_presence(status = discord.Status.online, activity=activity)

@bot.event
async def on_resumed():
    print("resume")
@bot.event
async def on_disconnect():
    print("disconnected")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    print(error)

async def reminder():
    tz = pytz.timezone('Australia/Melbourne')

    await bot.wait_until_ready()
    me = await bot.fetch_user(102054983381311488)
    while not bot.is_closed():
        if time(22, 56, 45) <= datetime.now(tz=tz).time() <= time(23,00, 15):
            await me.send("SINoALICE Collosseum!!!")
            await asyncio.sleep(240)

        print(f"Treshold time: {time(22, 56, 45)}")
        print(f"Current time:{datetime.now(tz=tz).time()}")
        await asyncio.sleep(30) # task runs every 60 seconds

#Loop this, have the tasks in a list (or use a function for lists of tasks)
task = bot.loop.create_task(reminder())
token = os.getenv("TOKEN")
loop = asyncio.get_event_loop()
try:
    print('starting')
    loop.run_until_complete(bot.start(token))
except KeyboardInterrupt:
    # cancel the list of tasks
    task.cancel()
    loop.run_until_complete(bot.logout())
except Exception as e:
    print(e)
    task.cancel()
finally:
    loop.close()