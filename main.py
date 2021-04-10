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


cards = []
card_search_dict = {}

@bot.command(aliases=["search", "sc", "card"])
async def search_card(ctx, *, msg):
    global cards
    global card_search_dict
    async with ctx.typing():
        url = f"https://www.trollandtoad.com/category.php?selected-cat=7061&search-words={msg.replace(' ', '+')}"
        resp = requests.get(url, headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'connection': 'kee-alive'
            },
            timeout=10)
        
        if(resp.status_code >= 400):
            await ctx.send(f"Failed to get a response from TrollandToad...")
            return 
        
        content = resp.text
        # print(resp.headers)
        tree = BeautifulSoup(content, features="lxml")
         

        card_list = tree.find('div', attrs={'class': 'result-container'})
        # Save All Cards in array.
        # build embed based on index
        # On msg react left/right, change index => change embed => edit msg
        cards = card_list.find_all('div', attrs={'class': 'product-col'})
        # print(f"cards, {cards}")
        embed = generate_embed_from_card(0, cards)
        
        m: discord.Message = await ctx.send(embed=embed)
        card_search_dict[m.id] = [0, cards]
        # print(f"card_search_dict, {card_search_dict}")

        if len(cards) > 1:
            await m.add_reaction("⬅️")
            await m.add_reaction("➡️")

    await edit_emeb_on_react(m)


async def edit_emeb_on_react(_m):
    def check(reaction, user: discord.User):
            return not user.bot and reaction.message.id in card_search_dict and reaction.message.id == _m.id and (str(reaction.emoji) == '➡️' or str(reaction.emoji) == '⬅️')
    print(f"ID: {_m.id}")
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=40.0, check=check)
    except asyncio.TimeoutError:
        card_search_dict.pop(_m.id , None)
        await _m.clear_reactions()
        # reaction.message.id  => clear from dict
    else:
        print("reacted to a message with card info")
        _cards = card_search_dict[reaction.message.id][1]
        if str(reaction.emoji) == '➡️':
            if card_search_dict[reaction.message.id][0] == len(_cards) - 1:
                card_search_dict[reaction.message.id][0] = 0
            else:
                card_search_dict[reaction.message.id][0] += 1

        elif str(reaction.emoji) == '⬅️':
            if card_search_dict[reaction.message.id][0] == 0:
                card_search_dict[reaction.message.id][0] = len(_cards) - 1
            else:
                card_search_dict[reaction.message.id][0] -= 1

        e = generate_embed_from_card(card_search_dict[reaction.message.id][0], _cards)

        await _m.edit(embed=e)
        await edit_emeb_on_react(_m)


#on react: if index == len(card) - 1 go to 0 
@search_card.error
async def search_card_error(ctx, error):
    await ctx.send('Couldn\'t retrieve card info...')


def generate_embed_from_card(index, cards_list):
    card = cards_list[index]
    card_name = card.find('a', attrs={'class': 'card-text'})

    img_link = card.find('img')['data-src']


    in_stock = True    
    price=card.find('div', attrs={'class': 'text-success'}).text
    if price == '$0.00':
        price=card.find('div', attrs={'class': 'text-info'}).text
        in_stock = False    


    desc = card.find('u').find('a').text
    embed = discord.Embed(title=card_name.text, url=f"https://www.trollandtoad.com/{card_name['href']}")
    embed.description = desc
    embed.add_field(name="Price", value=price, inline=True)
    embed.add_field(name="In Stock", value='✅' if in_stock else '❌', inline=True)

    embed.set_image(url=img_link)
    print("Hello")

    return embed


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