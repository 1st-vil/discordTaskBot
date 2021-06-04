import discord
import os
from os.path import join,dirname
from dotenv import load_dotenv
import redis

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
TOKEN=os.environ.get("TOKEN")

commandsAndDescriptions={
    '/nyan':'にゃーん',
    '/help':'コマンド一覧を表示する',
    '/echo [hoge]':'同じテキストを返す',

    '/add_me':'メッセージを送ったユーザーを追加する',
    '/delete_me':'メッセージを送ったユーザーを削除する',

    '/write [key] [value]':'キー"key"に"value"を書き込む',
    '/read [key]':'キー"key"の値を返す',
    '/read_all':'全てのキーとその値を返す',
    '/delete [key]':'キー"key"を削除する',
    '/delete_all':'全てのキーを削除する',
}
personalCommands=[
    '/write',
    '/read',
    '/read_all',
    '/delete',
    '/delete_all',
]

#-------------------------#

def connect_redis(db_id):
    return redis.from_url(url=os.environ.get('REDIS_URL'),decode_responses=True,db=db_id)

def delete_all_keys(user_id):
    db1=connect_redis(1)
    keys=db1.keys()
    for inner_key in keys:
        if inner_key[0:len(user_id)]==user_id:
            db1.delete(inner_key)

#-------------------------#

client=discord.Client()

@client.event
async def on_message(message):
    if message.author.bot:
        return
    user_id=str(message.author.id)
    user_name=message.author.name

    txt=message.content.split()
    if txt[0][0]!='/':
        pass
    elif txt[0]=='/nyan':
        await message.channel.send('にゃーん')
    elif txt[0]=='/help':
        res=''
        for command,description in commandsAndDescriptions.items():
            res+='{0}:{1}\n'.format(command,description)
        await message.channel.send(res)
    elif txt[0]=='/echo':
        if len(txt)==1:
            await message.channel.send('なんか言えや')
        else:
            await message.channel.send(' '.join(txt[1:]))

    elif txt[0]=='/add_me':
        db0=connect_redis(0)
        if user_id in db0.keys():
            await message.channel.send('既に追加されています')
        else:
            db0.set(user_id,user_name)
            await message.channel.send('ユーザー"{0}"(id"{1}")を追加しました'.format(user_name,user_id))
    elif txt[0]=='/delete_me':
        db0=connect_redis(0)
        if user_id in db0.keys():
            delete_all_keys(user_id)
            if db0.delete(user_id)==1:
                await message.channel.send('ユーザー"{0}"(id"{1}")を削除しました'.format(user_name,user_id))
            else:
                await message.channel.send('失敗しました')
        else:
            await message.channel.send('追加されていません')

    elif txt[0] in personalCommands:
        if not connect_redis(0).exists(user_id):
            await message.channel.send('ユーザーとして追加されていません')
            return
        db1=connect_redis(1)

        if txt[0]=='/write':
            if len(txt)==1:
                await message.channel.send('キーを指定してください')
                return
            if len(txt)==2:
                await message.channel.send('書き込む値を指定してください')
                return
            inner_key=user_id+txt[1]
            key=txt[1]
            val=' '.join(txt[2:])
            if db1.set(inner_key,val):
                await message.channel.send('キー"{0}"に"{1}"を書き込みました'.format(key,val))
            else:
                await message.channel.send('失敗しました')
        elif txt[0]=='/read':
            if len(txt)==1:
                await message.channel.send('キーを指定してください')
                return
            inner_key=user_id+txt[1]
            key=txt[1]
            if db1.exists(inner_key):
                await message.channel.send(db1.get(inner_key))
            else:
                await message.channel.send('キー"{0}"が存在しません'.format(key))
        elif txt[0]=='/read_all':
            res=''
            for inner_key in db1.keys():
                if inner_key[0:len(user_id)]==user_id:
                    res+='{0}:{1}\n'.format(inner_key[len(user_id):],db1.get(inner_key))
            if not res:
                res='empty'
            await message.channel.send(res)
        elif txt[0]=='/delete':
            if len(txt)==1:
                await message.channel.send('キーを指定してください')
                return
            inner_key=user_id+txt[1]
            key=txt[1]
            if db1.exists(inner_key):
                if db1.delete(inner_key)==1:
                    await message.channel.send('キー"{0}"を削除しました'.format(key))
                else:
                    await message.channel.send('失敗しました')
            else:
                await message.channel.send('キー"{0}"が存在しません'.format(key))
        elif txt[0]=='/delete_all':
            delete_all_keys(user_id)
            await message.channel.send('全てのキーを削除しました')
    else:
        await message.channel.send('コマンドが見つかりませんでした')

client.run(TOKEN)