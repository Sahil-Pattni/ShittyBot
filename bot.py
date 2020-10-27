import discord
import re
from discord.ext import commands
import time

# Global ID vars
TOKEN = 'NzcwMjEwNzg0Njg4NDcyMDY0.X5aQsA.xl2OE08jX9UwRRU_TiChsZNOxAI'
GUILD = 'Sad Dayz'
start_time = None
guild = None
# Modules
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    global start_time, guild
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(f'{bot.user.name} connected to {guild.name}')
    start_time = time.time()


# Upon a member joining
@bot.event
async def on_member_join(self, member):
    welcome_channel = discord.get(guild.channels, name='welcome')
    await welcome_channel.send(f'Hello there, {member.name}. Welcome to the {guild.name} discord!.')


@bot.event
async def on_message(message):
    # Avoid bot responding to itself
    if message.author == bot.user:
        return

    if message.channel.name == 'memes':
        def meme_reply(s):
            s = s.replace('*','').lower()
            if re.search(s, 'hello there!?'):
                return 'General Kenobi!'
            reply = ''
            switch = False
            for letter in s:
                reply += letter.upper() if switch else letter.lower()
                switch = not switch
            return reply
        await message.channel.send( meme_reply(message.content))
    # if message.channel.name == 'general':
    else:
        await bot.process_commands(message)


# Restriction channel check
def is_channel(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)


@bot.command(name='status', help='Returns bot statistics, such as uptime. Optional arguments are `minutes` and `hours`.')
async def status(ctx, arg=None):
    # if ctx.channel.name == 'bot_config':
    uptime = time.time() - start_time

    if arg is None:
        arg = 'seconds'

    arg = arg.lower()
    if re.search(arg, 'minutes?'):
        uptime /= 60
    elif re.search(arg, 'hours?'):
        uptime /= 3600

    arg = arg + 's' if arg[-1] != 's' else arg
    await ctx.send(f'Bot Uptime: {round(uptime, 2)} {arg}')

bot.run(TOKEN)


