import discord
from datetime import datetime as dt, timedelta

from functions import connect_redis, get_tasks
from info import *

intents=discord.Intents.default()
intents.members=True
client=discord.Client(intents=intents)

@client.event
async def on_ready():
    db0=connect_redis(0)
    for user_id in db0.keys():
        tasks=get_tasks(user_id,lambda x: x-dt.now()<timedelta(1))
        res=''
        for title,val in tasks:
            res+='{0} - {1}\n'.format(title,val)
        if res:
            await client.get_user(int(user_id)).send('{0}さんの登録している締切間近のタスク一覧:\n'.format(db0.get(user_id))+res)
        
client.run(TOKEN)