from discord.ext import commands
import requests
import discord
import random
import pickle
import os
import re

# Setup
env = os.environ
bot = commands.Bot(command_prefix='$')

# ----- Global Variables ----- #
GUILD_ID   = 747524804109664326
CHANNEL_ID = 747524804109664329
guild, channel = None, None

def remove_links(text):
    #return re.sub('(https?://)?(www.)([\d\w]+)(.[\w]+)((/[\d\w]+)+)?', '', text.strip())
    return text

async def get_chat_history(filepath, limit):
    messages = await channel.history(limit=limit).flatten()
    # Add input output as message -> reply
    antecedents = []
    consequents = []
    for i in reversed(range(1, len(messages))):
        a = remove_links(messages[i-1].content).strip()
        b = remove_links(messages[i].content).strip()
        if len(a) > 0 and len(b) > 0:
            antecedents.append(a)
            consequents.append(b)
    
    data = [antecedents, consequents]


    with open(filepath, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        await bot.logout()


# On initialization
@bot.event
async def on_ready():
    global guild, channel
    print('Connected and running...')
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    channel = discord.utils.get(guild.channels, id=CHANNEL_ID)

    limit = 10000
    await get_chat_history('data/message_log.pkl', limit)



# ------------------------------------ #
if __name__ == '__main__':
    print('Running main method....')
    bot.run(env.get('TOKEN'))