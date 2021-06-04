import discord
import os
from os.path import join,dirname
from dotenv import load_dotenv
import redis
import re
import datetime
from datetime import datetime as dt
import calendar

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
TOKEN=os.environ.get("TOKEN")

commandsAndDescriptions={
    '/nyan':'にゃーん',
    '/help':'コマンド一覧を表示する',
    '/echo [hoge]':'同じテキストを返す',

    '/add_me':'メッセージを送ったユーザーを追加する',
    '/delete_me':'メッセージを送ったユーザーを削除する',

    '/add [y/mo/d] [h:mi] [title]':'y年mo月d日h時mi分締切のタスク"title"を追加する',
    '/show_all':'追加されている全てのタスクを返す',
    '/delete [title]':'タスク"title"を削除する',
    '/delete_all':'全てのタスクを削除する',
}
personalCommands=[
    '/add',
    '/show_all',
    '/delete',
    '/delete_all',
]

#-------------------------#

def connect_redis(db_id):
    return redis.from_url(url=os.environ.get('REDIS_URL'),decode_responses=True,db=db_id)

def delete_all_tasks(user_id):
    db1=connect_redis(1)
    keys=db1.keys()
    for inner_key in keys:
        if inner_key[0:len(user_id)]==user_id:
            db1.delete(inner_key)

def valid_date_token(s):
    if not re.fullmatch(r'\d+/\d+/\d+',s):
        return False
    y,mo,d=map(int,s.split('/'))
    if y<datetime.MINYEAR or datetime.MAXYEAR<y:
        return False
    if mo<1 or 12<mo:
        return False
    if d<1 or calendar.monthrange(y,mo)[1]<d:
        return False
    return True
def valid_time_token(s):
    if not re.fullmatch(r'\d+:\d+',s):
        return False
    h,mi=map(int,s.split(':'))
    if h<0 or 23<h:
        return False
    if mi<0 or 59<mi:
        return False
    return True

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
            delete_all_tasks(user_id)
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

        if txt[0]=='/add':
            if len(txt)==1:
                await message.channel.send('締切日を指定してください')
                return
            if len(txt)==2:
                await message.channel.send('締切時刻を指定してください')
                return
            if len(txt)==3:
                await message.channel.send('タスク名を指定してください')
                return
            deadline_date=txt[1]
            deadline_time=txt[2]
            title=txt[3]
            inner_key=user_id+title
            if not valid_date_token(deadline_date):
                await message.channel.send('不正な締切日です')
            elif not valid_time_token(deadline_time):
                await message.channel.send('不正な締切時刻です')
            elif db1.exists(inner_key):
                await message.channel.send('タスク"{0}"は既に追加されています'.format(title))
            elif db1.set(inner_key,'{0} {1}'.format(deadline_date,deadline_time)):
                await message.channel.send('タスク"{0}"を追加しました\n締切日時 {1} {2}'.format(title,deadline_date,deadline_time))
            else:
                await message.channel.send('失敗しました')
        elif txt[0]=='/show_all':
            tasks=[]
            for inner_key in db1.keys():
                if inner_key[0:len(user_id)]==user_id:
                    title=inner_key[len(user_id):]
                    val=db1.get(inner_key)
                    y,mo,d_h_mi=val.split('/')
                    d,h_mi=d_h_mi.split(' ')
                    h,mi=h_mi.split(':')
                    y,mo,d,h,mi=map(int,[y,mo,d,h,mi])
                    tasks.append((dt(y,mo,d,h,mi),title,val))
            tasks.sort()
            res=''
            for d,title,val in tasks:
                res+='{0} - {1}\n'.format(title,val)
            if not res:
                res='empty'
            await message.channel.send(res)
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
            delete_all_tasks(user_id)
            await message.channel.send('全てのタスクを削除しました')
    else:
        await message.channel.send('コマンドが見つかりませんでした')

client.run(TOKEN)