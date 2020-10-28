import discord
import random
import re
from discord.ext import commands
import time
import psycopg2
from datetime import timedelta
import numpy as np
# Global ID vars
TOKEN = 'NzcwMjEwNzg0Njg4NDcyMDY0.X5aQsA.xl2OE08jX9UwRRU_TiChsZNOxAI'
GUILD = 'Carpool Gang' # Group / Guild Name
DB = 'hw_db' # PostGres DB
ADMIN = 'OVERLORD' # Admin Role Name
LOG_CHANNEL_NAME = 'bot_logs' # Channel for bot log output
WELCOME_CHANNEL_NAME = 'general' # Where the bot will welcome people
DB_URL = 'postgres://vfuuujvlhfnnel:3043f6cee923d7ca9995c49ce9d5f1a6488b4668148eaccabfe8bcd16ba05c01@ec2-35-168-54-239.compute-1.amazonaws.com:5432/d4crbc492gva03'
log_channel = None
start_time = None
guild = None
# Modules
bot = commands.Bot(command_prefix='$')
connection = None # PostgreSQL
cursor = None


# Log bot output
async def log(s):
    await log_channel.send(s)

# Init
@bot.event
async def on_ready():
    global log_channel, start_time, guild, connection, cursor
    guild = discord.utils.get(bot.guilds, name=GUILD)
    log_channel = discord.utils.get(guild.channels, name=LOG_CHANNEL_NAME)
    print(f'{bot.user.name} connected to {guild.name}')
    start_time = time.time()
    # Conntect to Postgres
    try:
        # connection = psycopg2.connect(user='sid', password='sloth',host='127.0.0.1',port='5432',database=DB)
        connection = psycopg2.connect(DB_URL, sslmode='require')
        cursor = connection.cursor()
        print('Connected to Postgres')
    except (Exception, psycopg2.Error) as error:
        print('Error while connectingto PostgreSQL', error)


# Upon a member joining
@bot.event
async def on_member_join(self, member):
    welcome_channel = discord.utils.get(guild.channels, name=WELCOME_CHANNEL_NAME)
    await welcome_channel.send(f'Hello there, {member.name}. Welcome to the {guild.name} discord!.')


# rEtUrNs TeXt ThAt LoOkS lIkE tHiS
def meme_reply(s):
    s = s.replace('*','').lower() # Take out star to avoid errors
    if re.search(s, 'hello tehre!?'):
        return 'General Kenobi!'
    reply = ''
    switch = False
    for letter in s:
        reply += letter.upper() if switch else letter.lower()
        switch = not switch
    return reply


# Handle messages
@bot.event
async def on_message(message):
    # Avoid bot responding to itself
    if message.author == bot.user:
        return
    # Meme Replies
    if message.channel.name == 'memes':
        await message.channel.send( meme_reply(message.content))
    # Handle commands
    else:
        await bot.process_commands(message)


# Restriction channel check
def is_channel(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)

# Status
@bot.command(name='uptime', help='Returns bot statistics, such as uptime.')
async def uptime(ctx, arg=None):
    output = ''
    uptime = str(timedelta(seconds=(time.time()-start_time))).split(':')
    uptime = [int(float(x)) for x in uptime]
    output += f'Bot Uptime: {uptime[0]} hours, {uptime[1]} minutes, {uptime[2]} seconds.'
    await ctx.send(output)

# Course deadlines
@bot.command(name='deadlines', help='Returns deadlines for course argument. If no argument, returns the deadlines for channel course')
async def deadlines(ctx, arg='DEFAULT'):
    query = 'SELECT * FROM deadlines WHERE course_code = '
    courses = ['F21BC', 'F21PA', 'F21DL', 'F21SA']
    channel = ctx.channel.name.upper()
    course_chosen = 'all courses'
    if arg.upper() == 'ALL' or (arg == 'DEFAULT' and channel not in courses):
        query = query[:23]
    elif arg is not None and arg != 'DEFAULT':
        arg = arg.upper()
        
        arg = arg.strip()
        if re.match('F20[A-Z]{2}', arg):
            arg = arg.replace('F20', 'F21')
        if arg not in courses:
            await ctx.send(f'Course code {arg} is invalid, try again.')
            return
        else:
            query += f'\'{arg}\''
            course_chosen = arg
    elif channel in courses:
        query += f'\'{channel}\''
        course_chosen = channel
    else:
        await ctx.send('Please provide a course code or \'all\' as an argument or run this command in a course-specific channel')
        return

    query += ' ORDER BY deadline'
    await log(f'Executing query:\n`{query}`')
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        await ctx.send('No deadlines to display.')
        return
    output = f'Deadlines for {course_chosen}:\n'
    for r in results:
        _, code, desc, date = r
        output += f'[{code}] {desc} on {date}\n'
    await ctx.send(output)


# To add deadlines via Discord
@bot.command(name='add_deadline', help='Format: !add_deadline COURSE_CODE, DESCRIPTION, DEADLINE (YYYY-MM-DD)')
@commands.has_role(ADMIN)
async def add_deadline(ctx, *args):
    error = ''
    if not re.match('F21[A-Z]{2}', args[0].upper()):
        error += f'Invalid course code format: {args[0].upper()}\n'
    if not re.match('20[2-9][0-9]-(0[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01])', args[-1]):
        error += f'Invalid date format. Expected YYYY-MM-DD'
    if len(error) > 0:
        await ctx.send(error)
        return
    desc = ''
    for x in range(1, len(args)-1):
        desc += f'{args[x]} '
    desc = desc.strip()
    query = f"INSERT INTO deadlines (course_code, description, deadline) VALUES ('{args[0]}', '{desc}', '{args[-1]}');"
    cursor.execute(query)
    connection.commit()
    await log(f'Executing query:\n`{query}`')
    await ctx.send(f'Successfully updated database. See #{LOG_CHANNEL_NAME} for more info.')


# Handle error if user not authorized
@add_deadline.error
async def add_error(error, ctx):
    if isinstance(error, commands.MissingRole):
        await ctx.send('Sorry, you don\'t have permission to modify the database.')


# Random picker
@bot.command(name='random', help='Chooses a random element from provided arguments')
async def rand_choose(ctx, *args):
    if len(args) == 0:
        await ctx.send('Please give me at least one item to choose from')
        return
    await ctx.send(f'I have chosen.....{random.choice(args)}.')


@bot.command(name='todo', help='To-Do List Functionality. No argument to see list, add XXXXXX to add, del X to delete')
async def todo(ctx, *args):
    cursor.execute('SELECT * FROM todo;')
    todo_list = [[id_val, desc] for user_id, id_val, desc in cursor.fetchall()]
    user_id = str(ctx.author.id)
    async def print_todo():
        global todo_list
        cursor.execute(f'SELECT * FROM todo where user_id = {user_id};')
        todo_list = [[id_val, desc] for user_id, id_val, desc in cursor.fetchall()]
        output = ''
        if len(todo_list) == 0:
            output = 'No Items'
        for i in range(len(todo_list)):
            output += f'{i+1}. {todo_list[i][1]}\n'
        await ctx.send(output)

    if len(args) == 0:
        await print_todo()
    elif args[0].lower() == 'add':
        if len(args) == 1:
            await ctx.send('Missing argument: Description')
            return
        desc = ''
        for i in range(1,len(args)):
            desc += f'{args[i]} '
        desc = desc.strip() # Remove trailing white space
        query = f"INSERT INTO todo (user_id, description) VALUES ({user_id}, '{desc}');"
        await log(f'Executing query:\n`{query}`')
        cursor.execute(query) # Insert into db
        connection.commit() # Commit changes
        await ctx.send('Added to-do item.')
        await print_todo()
        await ctx.send(f'See #{LOG_CHANNEL_NAME} for more details.')
    elif args[0].lower() == 'del':
        try:
            index = int(args[1])
            index -= 1
            res = todo_list[index][0]
            desc = todo_list[index][1]
            query = f'DELETE FROM todo WHERE ID = {res};'
            await log(f'Executing query:\n`{query}`')
            await ctx.send(f'Deleted item: {desc}\nUpdated DB: \n')
            cursor.execute(query)
            connection.commit() # Commit change
            await print_todo()
            await ctx.send(f'See #{LOG_CHANNEL_NAME} for more details.')
        except Exception as r:
            await ctx.send(f'Please provide an index for todo item to delete.\nError: {r}')


@bot.command(name='stats', help='gives statistics on a list of numbers')
async def stats(ctx, *args):
    def get_stats(data):
        output = 'STATISTICS\n--------------\n'
        data.sort()
        q1 = np.quantile(data, 0.25, interpolation='lower')
        q3 = np.quantile(data, 0.75, interpolation='higher')
        output += f'Mean: {round(data.mean(), 4)}\n'
        output += f'Median: {np.median(data)}\n'
        output += f'Mode: {np.argmax(data)}\n'
        output += f'Q1: {q1}\n'
        output += f'Q3: {q3}\n'
        output += f'IQR: {q3-q1}\n'
        output += f'Standard Deviation (Sample): {np.std(data, ddof=1)}\n'
        output += f'Standard Deviation (Population): {np.std(data)}\n----------------'
        return output
    try:
        data = np.array([float(x) for x in args])
        await ctx.send(get_stats)
        return

    except Exception as e:
        await ctx.send(f'Error processing input data. See #{LOG_CHANNEL_NAME} for more details.')
        await log(e)





# ------------------------------------ #
if __name__ == '__main__':
    print('Running main method....')
    bot.run(TOKEN)
