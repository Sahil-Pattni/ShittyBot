from feeds import get_news
from discord.ext import commands
import discord
import pickle
from random import randint
import os
from urllib.parse import urlparse
from random import randint
from reddit_joke import get_joke

# Setup
env = os.environ
bot = commands.Bot(command_prefix='$')

# ----- Global Variables ----- #
GUILD_ID   = 747524804109664326
GENERAL_CHANNEL = 806913959260323851
POLITICAL_CHANEL = 806624699635335208 # Real one
#POLITICAL_CHANEL = 805449044197507082 # bot_logs
guild, channel, politics = None, None, None

CATEGORIES = ['conservative', 'liberal', 'neutral']
LIMIT = 0.8

# WELCOME_MESSAGE = 'Guess who\'s back bitches? I\'ve been trained on 100,000 Reddit comments on an LSTM with ~3.3 million trainable parameters. Keep sending me messages, and if I detect a statement that leans on either political extreme, I\' be sure to let you know!'

def remove_links(text):
    text = text.strip()
    return '' if urlparse(text).scheme else text

async def get_chat_history(chnl, filepath, limit):
    messages = await chnl.history(limit=limit).flatten()
    data = []
    for m in messages:
        if m.author == bot.user:
            continue
        content = remove_links(m.content)
        if content != '':
            data.append(content)
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
        await bot.logout()


# On initialization
@bot.event
async def on_ready():
    print('Connected and running...')


@bot.command(name='news')
async def news(ctx):
    news = get_news()
    news = news[randint(0, len(news)-1)]
    embed = discord.Embed(title=f'BREAKING NEWS!\n\n{news.title}', url=news.link)
    await ctx.send(embed=embed)


@bot.command(name='joke')
async def joke(ctx):
    try:
        with open('jokes.txt', 'r') as jokes:
            jokes = jokes.read()
            jokes = jokes.split('<<>>')
            
            await ctx.send('\n'.join(jokes[randint(0, len(jokes)-1)].strip().split('<>')))
    except Exception as e:
        await ctx.send(f'Error: {e}')

@bot.command(name='jokes')
async def jokes(ctx):
    title, desc = get_joke()
    await ctx.send(f'{title}\n{desc}')

@bot.event
async def on_message(message):
    # Avoid bot responding to itself
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)
    # if message.channel.id in [GENERAL_CHANNEL]:
    #     await message.reply("HI")



#------------------------------------ #
if __name__ == '__main__':
    print('Running main method....')
    bot.run(env.get('DISCORD_TOKEN'))