import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.ext.tasks import loop
import asyncio
from datetime import datetime, time
import os
import pytz
from dotenv import load_dotenv
import random
import copy

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
        colo_time = os.getenv("COLO_TIME") 
        hms = colo_time.split(',')
        hour = int(hms[0]) or 22
        minute = int(hms[1]) or 00
        if time(hour, minute, 45) <= datetime.now(tz=tz).time() <= time(hour, minute + 2, 59):
            await me.send("SINoALICE Collosseum!!!")
            await asyncio.sleep(240)

        # print(f"Treshold time: {time(22, 56, 45)}")
        # print(f"Current time:{datetime.now(tz=tz).time()}")
        await asyncio.sleep(30) # task runs every 60 seconds

@bot.command()
async def colour(ctx):
    boiz = ctx.message.raw_mentions
    if not boiz: 
        return
    size = len(boiz)
    colours = ['Brown', 'Pink', 'Blue', 'White', 'Cyan', 'Red',
     'Purple', 'Orange', 'Yellow', 'Green', 'Black',
     'Light Green']

    random.shuffle(colours)
    colours = colours[0:size]
    names = copy.deepcopy(colours)
    random.shuffle(names)
    guild: discord.Guild = ctx.guild

    print_obj = []

    for boi in boiz:
        i = random.randint(0, size - 1)
        colour = colours.pop(i)
        name = names.pop(i)
        size -= 1
        member: discord.Member = await guild.fetch_member(boi)
        await member.send(f'**Name:** `{name}` || **Colour:** `{colour}`')
        print_obj.append(f"{member.username}: ")
        


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