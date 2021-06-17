import discord
from discord.ext import tasks

from functions import *
from info import *
from datetime import datetime as dt

intents=discord.Intents.default()
intents.members=True
client=discord.Client(intents=intents)

@tasks.loop(seconds=60)
async def notice():
    cur_jp=dt.now(timezone(timedelta(hours=9)))
    if cur_jp.strftime('%H:%M') in notice_time:
        db0=connect_redis(0)
        for user_id in db0.keys():
            delete_tasks(user_id,lambda x: x<cur_jp)
            res=''
            for title,val in get_tasks(user_id,lambda x: x-cur_jp<timedelta(1)):
                res+='{0} - {1}\n'.format(title,val)
            if res:
                await client.get_user(int(user_id)).send('{0}さんの登録している締切間近のタスク一覧:\n'.format(db0.get(user_id))+res)

@client.event
async def on_ready():
    notice.start()

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
        if len(txt)>1 and txt[1] in commandsAndDescriptions:
            return '{0}:{1}\n'.format(txt[1],commandsAndDescriptions[txt[1]])
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
            delete_tasks(user_id)
            if db0.delete(user_id)==1:
                await message.channel.send('ユーザー"{0}"(id"{1}")を削除しました'.format(user_name,user_id))
            else:
                await message.channel.send('失敗しました')
        else:
            await message.channel.send('ユーザーとして追加されていません')

    elif txt[0] in personalCommands:
        if not connect_redis(0).exists(user_id):
            await message.channel.send('ユーザーとして追加されていません')
            return
        db1=connect_redis(1)

        if txt[0]=='/add':
            if len(txt)<=3:
                await message.channel.send('不正な入力です')
                return
            deadline_date=txt[1]
            deadline_time=txt[2]
            title=txt[3]
            inner_key=user_id+title
            if not valid_date_token(deadline_date) or not valid_time_token(deadline_time):
                await message.channel.send('不正な入力です')
                return
            deadline_str='{0} {1}'.format(deadline_date,deadline_time)
            y,mo,d,h,mi=token_to_datetime(deadline_str)
            deadline=dt(y,mo,d,h,mi,tzinfo=timezone(timedelta(hours=9)))
            if deadline<dt.now(timezone(timedelta(hours=9))):
                await message.channel.send('既に締切を過ぎています')
            elif db1.exists(inner_key):
                await message.channel.send('タスク"{0}"は既に追加されています'.format(title))
            elif db1.set(inner_key,deadline_str):
                await message.channel.send('タスク"{0}"を追加しました\n締切 {1}'.format(title,deadline_str))
            else:
                await message.channel.send('失敗しました')
        elif txt[0]=='/show_all':
            delete_tasks(user_id,lambda x: x<dt.now(timezone(timedelta(hours=9))))
            tasks=get_tasks(user_id)
            res=''
            for title,val in tasks:
                res+='{0} - {1}\n'.format(title,val)
            if not res:
                res='empty'
            await message.channel.send('{0}さんの登録しているタスク一覧:\n'.format(user_name)+res)
        elif txt[0]=='/delete':
            if len(txt)==1:
                await message.channel.send('タスク名を指定してください')
                return
            inner_key=user_id+txt[1]
            title=txt[1]
            if db1.exists(inner_key):
                if db1.delete(inner_key)==1:
                    await message.channel.send('タスク"{0}"を削除しました'.format(title))
                else:
                    await message.channel.send('失敗しました')
            else:
                await message.channel.send('タスク"{0}"が存在しません'.format(title))
        elif txt[0]=='/delete_all':
            delete_tasks(user_id)
            await message.channel.send('全てのタスクを削除しました')
    else:
        await message.channel.send('コマンドが見つかりませんでした\n/help でコマンド一覧を確認してください')

client.run(TOKEN)