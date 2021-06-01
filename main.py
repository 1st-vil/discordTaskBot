import discord

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
TOKEN=os.environ.get("TOKEN")

client = discord.Client()

@client.event
async def on_message(message):
    if message.author.bot:
        return

    res=message.content.split()
    if res[0] == '/neko':
        await message.channel.send('にゃーん')

client.run(TOKEN)