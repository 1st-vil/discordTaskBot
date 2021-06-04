import discord
import os
from os.path import join,dirname
from dotenv import load_dotenv
import redis

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
TOKEN=os.environ.get("TOKEN")

#-------------------------#

def connect_redis(db_id):
    return redis.from_url(url=os.environ.get('REDIS_URL'),decode_responses=True,db=db_id)

#-------------------------#

intents=discord.Intents.default()
intents.members=True
client=discord.Client(intents=intents)

@client.event
async def on_ready():
    db0=connect_redis(0)
    db1=connect_redis(1)
    for user_id in db0.keys():
        res="{0}さんの登録しているキーと値の一覧:\n".format(db0.get(user_id))
        for inner_key in db1.keys():
            if inner_key[:len(user_id)]==user_id:
                res+='{0}:{1}\n'.format(inner_key[len(user_id):],db1.get(inner_key))
        await client.get_user(int(user_id)).send(res)
        
client.run(TOKEN)