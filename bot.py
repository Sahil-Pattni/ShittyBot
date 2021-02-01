from urllib.parse import urlencode # Used for authenticated requests (see: Binance module)
from ApiError import ApiError # Custom Binance API Exception
from discord.ext import commands
import requests
import discord
import hashlib # Used for signed requests
import random
import hmac # Used for signed requests
import os # Environment variables
import re # Regex
import binance


# Environment with access tokens
env = os.environ

# Global ID vars
LOG_CHANNEL_NAME = 'bot_logs' # Channel for bot log output
WELCOME_CHANNEL_NAME = 'general' # Where the bot will welcome people
VINAYAK = 713761220154621992 # Vinayak's ID
SAHIL = 346393129915777034 # My ID
BANNED_CHANNELS = ['trivia', 'chess', 'nsfw'] # Channels to ignore

# Modules
guild = None # Discord Group
log_channel = None
bot = commands.Bot(command_prefix='$')


# Output to bot_log channel
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
    if 'dummy' in message.content.lower().split(' '):
        if message.author.id == VINAYAK:
            await message.channel.send("Bonk! You are not allowed to say `dummy`.")
    
    # Handle commands
    else:
        await bot.process_commands(message)



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
    

# Retrieve Binance portfolio
@bot.command(name='stonks', help='stonks')
async def stonks(ctx):
    
    # Only allow me to use it for now
    if ctx.author.id != SAHIL:
        await ctx.send(f'{ctx.author.name}, you are not authorized to use stonks!')

    free, locked = binance.get_balances()
    
    # Prepare string reply for message
    reply = 'FREE BALANCES:'
    for asst in free:
        reply += f"{asst[1]:,.3f} {asst[0]} ({asst[2]:,.3f} USDT)\n"
    
    reply += '\nOPEN ORDERS:'
    for asst in locked:
        reply += f"{asst[1]:,.3f} {asst[0]} ({asst[2]:,.3f} USDT)\n"
    
    total_usdt = sum([x[2] for x in free]) + sum(x[2] for x in locked)

    reply += f'\nTotal Asset Worth (USDT): ${total_usdt:,.2f}'

    await ctx.send(reply) # send
    return


# ------------------------------------ #
if __name__ == '__main__':
    print('Running main method....')
    bot.run(env.get('TOKEN'))
