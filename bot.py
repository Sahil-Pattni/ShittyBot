from urllib.parse import urlencode # Used for authenticated requests (see: Binance module)
from discord.ext import commands
import requests
import discord
import hashlib # Used for signed requests
import random
import hmac # Used for signed requests
import os # Environment variables
import re # Regex


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
@bot.command(name='price', help='crypto pair prices')
async def price(ctx, *args):
    if len(args) == 0:
        await ctx.send("Please provide a ticker symbol (e.g. BTC USTD for BTC/USDT)")
        return
    
    elif len(args) < 2:
        await ctx.send("Please provide a currency pair.")
        return
    
    # Inform user if they provide more than two args
    elif len(args) > 2:
        await ctx.send(f'Assuming {args[0]}/{args[1]} as ticker pair...')

    url = 'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': f'{args[0]}{args[1]}'}
    print(params)
    response = requests.get(url, params=params).json()

    # Check for error
    if 'code' in response:
        await ctx.send(response['msg'])
    # Return Price
    else:
        await ctx.send(f"1 {args[0]} = {float(response['price']):.4f} {args[1]}")
    
# Retrieve Binance portfolio
@bot.command(name='stonks', help='stonks')
async def stonks(ctx, *args):
    
    # Only allow me to use it for now
    if ctx.author.id != SAHIL:
        await ctx.send(f'{ctx.author.name}, you are not authorized to use stonks!')

    base = 'https://api.binance.com/api'
    timestamp = int(requests.get(f'{base}/v1/time').json()['serverTime'])
    params = {
        'timestamp': timestamp
    }

    
    # Get signed payload
    hashsign = hmac.new(
        env.get('BINANCE_SECRET').encode('utf-8'),
        urlencode(params).encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    # Add signature to request parameters
    params['signature'] = hashsign
    # Add API key to headers
    headers = {'X-MBX-APIKEY': env.get('BINANCE_KEY')}

    # ------ ARGUMENTS TAKEN OUT FOR NOW ---------- #

    # --------- OPEN ORDERS ------------- #
    if False:
        # TODO: Implement
        await ctx.send('To be implemented')
        return


    # -------- ACCOUNT BALANCES ---------- #
    elif True:
        reply = ''
        response = requests.get(f"{base}/v3/account", params=params, headers=headers).json()
        
        # Handle errors
        if 'code' in response:
            await ctx.send(f"Error encountered. See #{LOG_CHANNEL_NAME} for details.")
            await log(f"Error on command: `{ctx.message.content}`. Error: {response['msg']}")
        
        # Return balances

        # total USDT counter
        total_usdt = 0

        assets = [] # Store crypto values here

        for crypto in response['balances']:
            symbol, free, locked = crypto['asset'], float(crypto['free']), float(crypto['locked'])
            # Skip empty wallets
            if free == 0:
                continue

            conversion_rate = 1 # Default if currency is USDT

            # Calculate conversion rate if not USDT
            if symbol != 'USDT':
                # Get ticker pair price
                rate = requests.get(
                    f'{base}/v3/ticker/price',
                    params={'symbol': f'{symbol}USDT'}
                ).json()

                # Handle server-side error and exit
                if 'code' in rate:
                    await ctx.send(f"Error encountered. See #{LOG_CHANNEL_NAME} for details.")
                    await log(f"Error on command: `{ctx.message.content}`. Error: {rate['msg']}")
                    return
                # Set conversion rate
                conversion_rate = float(rate['price'])

            # Add to assets list [SYMBOL, QTY, USDT_EQUIVALENT]
            assets.append([symbol, free, free * conversion_rate])
        
        total_usdt = sum([x[2] for x in assets]) # Total worth in USDT (real-time)
        assets.sort(key=lambda x: x[2]) # Sort by total USDT value

        # Prepare string reply for message
        for asst in assets:
            reply += f"{asst[1]:,.3f} {asst[0]} ({asst[2]:,.3f} USDT)\n"
        reply += f'\nTotal Asset Worth (USDT): ${total_usdt:,.2f}'

        await ctx.send(reply) # send
        return



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
