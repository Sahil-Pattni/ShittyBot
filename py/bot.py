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
from reactions import emoji_map

# Environment with access tokens
env = os.environ

# Global ID vars
LOG_CHANNEL_NAME = 'bot_logs' # Channel for bot log output
WELCOME_CHANNEL_NAME = 'general' # Where the bot will welcome people
VINAYAK = 713761220154621992 # Vinayak's ID
SAHIL = 346393129915777034 # My ID
BANNED_CHANNELS = ['trivia', 'chess', 'nsfw'] # Channels to ignore
DEBUG_GUILD = 806913959260323848 

# Modules
bot = commands.Bot(command_prefix='$')


# Log messages to guild's log channel
async def log(message, guild):
    log_channel = discord.utils.get(guild.channels, name=LOG_CHANNEL_NAME)
    await log_channel.send(message)


# On initialization
@bot.event
async def on_ready():
    print('Connected and running...')

# Handle messages
@bot.event
async def on_message(message):
    # Ignore these channels
    if message.channel.name.lower() in BANNED_CHANNELS:
        return

    # Avoid bot responding to itself
    if message.author == bot.user:
        return

    # Iterate through words and check for matches
    for word in emoji_map:
        if word in message.content.lower():
            reaction = emoji_map[word]
            await message.add_reaction(discord.utils.get(bot.emojis, name=reaction))
    # Handle commands
    else:
        await bot.process_commands(message)


# Report deleted messages 
@bot.event
async def on_message_delete(message):
    # avoid recursive deletion messages
    if message.author == bot.user:
        return
    await message.channel.send(f'{message.author} deleted the following message:\n"{message.content}"')



# Random picker
@bot.command(name='random', help='Chooses a random element from provided arguments')
async def rand_choose(ctx, *args):
    if len(args) == 0:
        await ctx.send('Please give me at least one item to choose from')
        return
    await ctx.send(f'I have chosen.....{random.choice(args)}.')


# Insult
@bot.command(name='insult', help='insults you')
async def insult(ctx, *args):
    BASE = 'https://insult.mattbas.org/api/'
    params = {}
    # If arguments exist, use them
    params['who'] = ctx.message.content.replace('$insult ', '')
    # Get custom insult
    insult = requests.get(f'{BASE}/insult', params=params).text

    await ctx.send(insult)
        

# Retrieve Binance portfolio
@bot.command(name='stonks', help='stonks')
async def stonks(ctx):
    
    # Only allow me to use it for now
    if ctx.author.id != SAHIL:
        await ctx.send(f'{ctx.author.name}, you are not authorized to use stonks!')

    try:
        free, locked = binance.get_balances()
    except ApiError as e:
        await ctx.send("Error encountered. Please see #bot_logs for further details.")
        await log(f'Error on {ctx.message.content}:\n{e}', ctx.guild)
        return
    
    # Prepare string reply for message
    reply = 'Available Funds:\n'
    for asst in free:
        # Don't print any assets with < 1 USDT balance
        if asst[2] > 1:
            change = asst[3]
            sign = '+' if change > 0 else '' # add + if positive change
            change = f'{sign}{change:.2f}%' # String format
            reply += f"{asst[1]:,.3f} {asst[0]} [{change}] ({asst[2]:,.3f} USDT)\n"
    
    reply += '\nFunds locked in unfulfilled orders:\n'
    for asst in locked:
        if asst[2] > 1:
            change = asst[3]
            sign = '+' if change > 0 else '' # add + if positive change
            change = f'{sign}{change:.2f}%' # String format
            reply += f"{asst[1]:,.3f} {asst[0]} [{change}] ({asst[2]:,.3f} USDT)\n"
    
    total_usdt = sum([x[2] for x in free]) + sum(x[2] for x in locked)

    reply += f'\nTotal Asset Worth (USDT): ${total_usdt:,.2f}'

    await ctx.send(reply) # send
    return


# ------------------------------------ #
if __name__ == '__main__':
    print('Running main method....')
    bot.run(env.get('TOKEN'))
