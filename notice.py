import discord
import os
from os.path import join,dirname
from dotenv import load_dotenv
import redis
from datetime import datetime as dt, timedelta

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
TOKEN=os.environ.get("TOKEN")

#-------------------------#

def connect_redis(db_id):
    return redis.from_url(url=os.environ.get('REDIS_URL'),decode_responses=True,db=db_id)
def token_to_datetime(val):
    y,mo,d_h_mi=val.split('/')
    d,h_mi=d_h_mi.split(' ')
    h,mi=h_mi.split(':')
    return map(int,[y,mo,d,h,mi])

#-------------------------#

intents=discord.Intents.default()
intents.members=True
client=discord.Client(intents=intents)

@client.event
async def on_ready():
    db0=connect_redis(0)
    db1=connect_redis(1)
    for user_id in db0.keys():
        tasks=[]
        for inner_key in db1.keys():
            if inner_key[:len(user_id)]==user_id:
                title=inner_key[len(user_id):]
                val=db1.get(inner_key)
                y,mo,d,h,mi=token_to_datetime(val)
                deadline=dt(y,mo,d,h,mi)
                if deadline-dt.now()<timedelta(1):
                    tasks.append((deadline,title,val))
        tasks.sort()
        res=''
        for d,title,val in tasks:
            res+='{0} - {1}\n'.format(title,val)
        if not res:
            res='empty'
        await client.get_user(int(user_id)).send('{0}さんの登録している締切間近のタスク一覧:\n'.format(db0.get(user_id))+res)
        
client.run(TOKEN)