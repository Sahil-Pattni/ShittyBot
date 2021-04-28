from discord.ext import commands
import discord
import pickle
import os
from urllib.parse import urlparse
from predictor import predict
import numpy as np


# Setup
env = os.environ
bot = commands.Bot(command_prefix='$')

# ----- Global Variables ----- #
GUILD_ID   = 747524804109664326
GENERAL_CHANNEL = 747524804109664329
POLITICAL_CHANEL = 806624699635335208 # Real one
#POLITICAL_CHANEL = 805449044197507082 # bot_logs
guild, channel, politics = None, None, None

CATEGORIES = ['conservative', 'liberal', 'neutral']
LIMIT = 0.8

WELCOME_MESSAGE = 'Guess who\'s back bitches? I\'ve been trained on 100,000 Reddit comments on an LSTM with ~3.3 million trainable parameters. Keep sending me messages, and if I detect a statement that leans on either political extreme, I\' be sure to let you know!'

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
    global guild, channel, politics
    print('Connected and running...')
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    channel = discord.utils.get(guild.channels, id=GENERAL_CHANNEL)
    politics = discord.utils.get(guild.channels, id=POLITICAL_CHANEL)

    limit = 1000
    await channel.send(WELCOME_MESSAGE)
    # await get_chat_history(politics, f'/Users/sloth_mini/Documents/Discord_Bot/data/message_log_{politics.name}.pkl', limit)

@bot.event
async def on_message(message):
    # Avoid bot responding to itself
    if message.author == bot.user:
        return
    if message.channel.id in [GENERAL_CHANNEL, POLITICAL_CHANEL]:
        scores = predict(message.content)
        if scores is not None:
            value = max(scores)
            if value < LIMIT:
                return
            tag = CATEGORIES[np.argmax(scores)]
            reply = f'I am {value*100:,.2f}% sure this is a {tag} statement.'
            await message.reply(reply)



#------------------------------------ #
if __name__ == '__main__':
    print('Running main method....')
    bot.run(env.get('TOKEN'))