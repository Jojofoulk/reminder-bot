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
from datetime import datetime, timedelta
import pytz

import requests
import html
from bs4 import BeautifulSoup 

load_dotenv()

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Bot running")
    activity = discord.Activity(name=f'Cöck', type=discord.ActivityType.playing)
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


@bot.command(aliases=["search", "sc", "card"])
async def search_card(ctx, *, msg):
    async with ctx.typing():
        url = f"https://www.trollandtoad.com/category.php?selected-cat=7061&search-words={msg.replace(' ', '+')}"
        resp = requests.get(url, headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'})
        content = resp.text
        tree = BeautifulSoup(content, features="lxml")

        card_list = tree.find('div', attrs={'class': 'result-container'})
        # Save All Cards in array.
        # build embed based on index
        # On msg react left/right, change index => change embed => edit msg
        card = card_list.find('div', attrs={'class': 'product-col'})

        card_name = card.find('a', attrs={'class': 'card-text'})

        img_link = card.find('img')['data-src']

        price=card.find('div', attrs={'class': 'text-success'}).text
        desc = card.find('u').find('a').text
        embed = discord.Embed(title=card_name.text, url=f"https://www.trollandtoad.com/{card_name['href']}")
        embed.description = desc
        embed.add_field(name="Price", value=price, inline=False)
        embed.set_image(url=img_link)
        print("Hello")
        await ctx.send(embed=embed)

@search_card.error
async def search_card_error(ctx, error):
    await ctx.send('Couldn\'t retrieve card info...')



async def reminder():
    tz = pytz.timezone('Australia/Melbourne')
    await bot.wait_until_ready()
    me = await bot.fetch_user(102054983381311488)
    while not bot.is_closed():
        colo_time = os.getenv("COLO_TIME") 
        hms = colo_time.split(',')
        hour = int(hms[0]) or 22
        minute = int(hms[1]) or 00

        p_hour = hour
        p_minute = minute - 3
        if minute < 3:
            p_minute = 60 - minute
            p_hour = hour - 1

        if time(p_hour, p_minute, 00) <= datetime.now(tz=tz).time() <= time(hour, minute, 00):
            await me.send("SINoALICE Collosseum!!!")
            await asyncio.sleep(240)

        # print(f"Treshold time: {time(22, 56, 45)}")
        # print(f"Current time:{datetime.now(tz=tz).time()}")
        await asyncio.sleep(30) # task runs every 60 seconds

def dm_only():
    async def predicate(ctx):
        if ctx.guild is not None:
            return False
        return True
    return commands.check(predicate)

def is_me():
    async def predicate(ctx):
        return int(ctx.author.id) == int(os.getenv("ME"))
    return commands.check(predicate)

@bot.command(aliases=["colotime"])
@dm_only()
@is_me()
async def check_time(ctx):
    colo_time = os.getenv("COLO_TIME")
    hour = colo_time[0:2]
    minutes = colo_time[3:5]

    FMT = '%H:%M:%S'
    s1 = f'{hour}:{minutes}:00'

    s2 = datetime.now(pytz.timezone('Australia/Melbourne')).strftime(FMT)
    tdelta = datetime.strptime(s1, FMT) - datetime.strptime(s2, FMT)
    if tdelta.days < 0:
        tdelta = timedelta(days=0, seconds=tdelta.seconds, microseconds=tdelta.microseconds)
    
    await ctx.send(f"Time until next colo: **{tdelta}s** \n*Planned time {s1} AEDT*")

@bot.command(aliases=["setcolotime"])
@dm_only()
@is_me()
async def change_time(ctx, msg):
    os.environ["COLO_TIME"] = msg

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