import discord
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
TOKEN=os.environ.get("TOKEN")

commands={
    '/nyan':'にゃーん',
    '/help':'コマンド一覧を表示する',
    '/echo [hoge]':'同じテキストを送り返す',
}

#-------------------------#

client=discord.Client()

@client.event
async def on_message(message):
    if message.author.bot:
        return

    txt=message.content.split()
    if txt[0][0]!='/':
        pass
    elif txt[0]=='/nyan':
        await message.channel.send('にゃーん')
    elif txt[0]=='/help':
        res=''
        for command,description in commands.items():
            res+=command+' : '+description+'\n'
        await message.channel.send(res)
    elif txt[0]=='/echo':
        await message.channel.send(' '.join(txt[1:]))
    else:
        await message.channel.send('command not found')

client.run(TOKEN)