import discord
import os
from os.path import join,dirname
from dotenv import load_dotenv
import redis

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
TOKEN=os.environ.get("TOKEN")

commands={
    '/nyan':'にゃーん',
    '/help':'コマンド一覧を表示する',
    '/echo [hoge]':'同じテキストを返す',
    '/write [key] [value]':'キー"key"に"value"を書き込む',
    '/read [key]':'キー"key"の値を返す',
    '/read_all':'全てのキーとその値を返す',
    '/delete [key]':'キー"key"を削除する',
    '/delete_all':'全てのキーを削除する',
}

#-------------------------#

def connect_redis():
    return redis.from_url(url=os.environ.get('REDIS_URL'),decode_responses=True)

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
    elif txt[0]=='/write':
        if len(txt)==1:
            await message.channel.send('キーを指定してください')
            return
        if len(txt)==2:
            await message.channel.send('書き込む値を指定してください')
            return
        key=txt[1]
        val=' '.join(txt[2:])
        conn=connect_redis()
        if conn.set(key,val):
            await message.channel.send('キー"{0}"に"{1}"を書き込みました'.format(key,val))
        else:
            await message.channel.send('失敗しました')
    elif txt[0]=='/read':
        if len(txt)==1:
            await message.channel.send('キーを指定してください')
            return
        key=txt[1]
        conn=connect_redis()
        if conn.exists(key):
            await message.channel.send(conn.get(key))
        else:
            await message.channel.send('キー"{0}"が存在しません'.format(key))
    elif txt[0]=='/read_all':
        res=''
        conn=connect_redis()
        for key in conn.keys():
            res+='{0}:{1}\n'.format(key,conn.get(key))
        if not res:
            res='empty'
        await message.channel.send(res)
    elif txt[0]=='/delete':
        if len(txt)==1:
            await message.channel.send('キーを指定してください')
            return
        key=txt[1]
        conn=connect_redis()
        if conn.exists(key):
            if conn.delete(key)==1:
                await message.channel.send('キー"{0}"を削除しました'.format(key))
            else:
                await message.channel.send('失敗しました')
        else:
            await message.channel.send('キー"{0}"が存在しません'.format(key))
    elif txt[0]=='/delete_all':
        conn=connect_redis()
        conn.flushdb()
        await message.channel.send('全てのキーを削除しました')
    else:
        await message.channel.send('コマンドが見つかりませんでした')

client.run(TOKEN)