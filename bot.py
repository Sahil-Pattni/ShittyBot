import requests
import discord
from discord.ext import commands
import random
import re
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
VINAYAK = 713761220154621992 # Vinayak's ID
BANNED_CHANNELS = ['trivia', 'chess', 'nsfw'] # Channels to ignore

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
    log_channel = discord.utils.get(guild.channels, name=LOG_CHANNEL_NAME)
    print(f'{bot.user.name} connected to {guild.name}')

# Upon a member joining
@bot.event
async def on_member_join(self, member):
    welcome_channel = discord.utils.get(guild.channels, name=WELCOME_CHANNEL_NAME)
    await welcome_channel.send(f'Hello there, {member.name}. Welcome to the {guild.name} discord!.')

# Handle messages
@bot.event
async def on_message(message):
    # Ignore these channels
    if message.channel.name.lower() in BANNED_CHANNELS:
        return

    # Avoid bot responding to itself
    if message.author == bot.user:
        return

    # Stop Vinayak from saying dummy
    if message.author.id == VINAYAK:
        if 'dummy' in message.content.lower().split(' '):
            await message.channel.send("Bonk! You are not allowed to say `dummy`.")
    
    # Handle commands
    else:
        await bot.process_commands(message)


# Restriction channel check
def is_channel(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)


# Checks if a user is allowed to say dummy
@bot.command(name='dummycheck', help='Can u use the word dummy?')
async def dummy_check(ctx):
    flag = ''
    if ctx.author.id == VINAYAK:
        flag = 'NOT'
    await ctx.send(f'{ctx.author.name}, you are {flag} allowed to say the word dummy.')


# Random picker
@bot.command(name='random', help='Chooses a random element from provided arguments')
async def rand_choose(ctx, *args):
    if len(args) == 0:
        await ctx.send('Please give me at least one item to choose from')
        return
    await ctx.send(f'I have chosen.....{random.choice(args)}.')


# Insult
@bot.command(name='insult', help='insults you')
async def insult(ctx):
    response = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
    await ctx.send(response.json()['insult'])


# Get cryptocurrency pair price via Binance
@bot.command(name='price', help='binance api')
async def price(ctx, *args):
    if len(args) == 0:
        await ctx.send("Please provide a ticker symbol (e.g. BTC USTD for BTC/USDT)")
        return
    
    # Inform user if they provide more than two args
    elif len(args) > 2:
        await ctx.send(f'Assuming {args[0]}/{args[1]} as ticker pair...')

    url = 'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': f'{args[0]}{args[1]}'}
    response = requests.get(url, params=params).json()

    # Check for error
    if 'code' in response:
        await ctx.send(response['msg'])
    # Return Price
    else:
        await ctx.send(f"1 {args[0]} = {response['price']:.4f} {args[1]}")
        
    

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
