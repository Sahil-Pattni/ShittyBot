import discord
import re

TOKEN = 'NzcwMjEwNzg0Njg4NDcyMDY0.X5aQsA.xT-m61pWWZwvOBWuy6YQ_FhqWJ8'
GUILD = 'Carpool Gang'


class DiscordClient(discord.Client):
    # Global vars
    guild = None

    # Upon initialization of bot
    async def on_ready(self):
        global guild
        guild = discord.utils.get(client.guilds, name=GUILD)
        print(f'{client.user} has connected to {guild.name}')


    # Upon a member joining
    async def on_member_join(self, member):
        welcome_channel = discord.get(guild.channels, name='welcome')
        await welcome_channel.send(f'Hello there, {member.name}. Welcome to the {guild.name} discord!.')


    # Upon a message being sent
    async def on_message(self, message):
        # Skip if bot message
        if message.author == client.user:
            return

        if message.channel.name == 'general':
            response = self.general_response(message.content)
            if response:
                await message.channel.send(response)
        else:
            pass # Don't respond

    def general_response(self, content):
        if re.match(content.lower(), 'hello there!?'):
            return 'General Kenobi'
        else:
            return

client = DiscordClient()
client.run(TOKEN)
