import requests
import discord
import random
import re
from discord.ext import commands
import time
import psycopg2
import datetime
from datetime import timedelta
import numpy as np
import os

# Environment with access tokens
env = os.environ

# Global ID vars
LOG_CHANNEL_NAME = 'bot_logs' # Channel for bot log output
WELCOME_CHANNEL_NAME = 'general' # Where the bot will welcome people

# Modules
guild = None # Discord Group
log_channel = None
bot = commands.Bot(command_prefix='$')


# Log bot output
async def log(s):
    await log_channel.send(s)

# Init
@bot.event
async def on_ready():
    global log_channel, start_time, guild, connection, cursor
    guild = discord.utils.get(bot.guilds, id=747524804109664326)
    log_channel = discord.utils.get(guild.channels, name='LOG_CHANNEL_NAME')
    print(f'{bot.user.name} connected to {guild.name}')


# Upon a member joining
@bot.event
async def on_member_join(self, member):
    welcome_channel = discord.utils.get(guild.channels, name=WELCOME_CHANNEL_NAME)
    await welcome_channel.send(f'Hello there, {member.name}. Welcome to the {guild.name} discord!.')


# rEtUrNs TeXt ThAt LoOkS lIkE tHiS
def meme_reply(s):
    s = s.replace('*','').lower() # Take out star to avoid errors
    reply = ''
    switch = False
    for letter in s:
        reply += letter.upper() if switch else letter.lower()
        switch = not switch
    
    # url point for meme api
    url = 'https://api.imgflip.com/caption_image'
    # template ID for mocking spongebob meme
    spongebob_id = 102156234

    params = {
        'template_id': spongebob_id,
        'text1': WoW,
        'username': env.get('IMGFLIP_USERNAME'),
        'password': env.get('IMGFLIP_PASSWORD')
    }

    response = requests.get(url, params=params)
    response = response.json()

    if response['success'] == False:
        log(f'Error with meme reply: {response['error_message']}')
    
    return response['data']['url']


# Handle messages
@bot.event
async def on_message(message):
    # Avoid bot responding to itself
    if message.author == bot.user:
        return
    # Meme Replies
    if message.channel.name == 'general':
        # If message begins with wow
        if message.content.lower().strip()[:3] == 'wow':
            await message.channel.send(meme_reply(message.content))
    # Handle commands
    else:
        await bot.process_commands(message)


# Restriction channel check
def is_channel(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)


# Random picker
@bot.command(name='random', help='Chooses a random element from provided arguments')
async def rand_choose(ctx, *args):
    if len(args) == 0:
        await ctx.send('Please give me at least one item to choose from')
        return
    await ctx.send(f'I have chosen.....{random.choice(args)}.')


@bot.command(name='insult', help='insults you')
async def insult(ctx):
    response = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
    await ctx.send(response.json()['insult'])


@bot.command(name='btc', help='btc_price')
async def btc(ctx):
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    response = requests.get(url).json()['bpi']['USD']['rate']
    await ctx.send(f'Current Price: ${response}')


@bot.command(name='doge', help='dogecoin price')
async def btc(ctx):
    url = f'https://api.nomics.com/v1/currencies/ticker?key={env.get('NOMICS_KEY')}&ids=DOGE&attributes=price'
    response = requests.get(url).json()[0]['price']
    await ctx.send(f'Current Price: ${response}')

# Wallpaper Generator
# Optional arguments: width, height
@bot.command(name='wallpaper', help='Wallpaper')
async def wallpaper(ctx, *args):
    w = 1920
    h = 1080
    try:
        if len(args) == 1:
            x = int(args[0])
            w = x
            h = x
        elif len(args) == 2:
            w = int(args[0])
            h = int(args[1])
    except Exception as e:
        await ctx.send(f'Your arguments are invalid. Please try 0-2 integer arguments.\nSee #{LOG_CHANNEL_NAME} for more details.')
        await log(e)
        return

    seed = random.randint(10,999999)
    url = f'https://picsum.photos/seed/{seed}/{w}/{h}'
    await ctx.send(url)

# ------------------------------------ #
if __name__ == '__main__':
    print('Running main method....')
    bot.run(env.get('TOKEN'))
