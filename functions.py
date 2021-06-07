import os
import redis
import re
import datetime
from datetime import datetime as dt
import calendar

def connect_redis(db_id):
    return redis.from_url(url=os.environ.get('REDIS_URL'),decode_responses=True,db=db_id)
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
def token_to_datetime(val):
    y,mo,d_h_mi=val.split('/')
    d,h_mi=d_h_mi.split(' ')
    h,mi=h_mi.split(':')
    return map(int,[y,mo,d,h,mi])
def get_tasks(user_id,fil=lambda x: True):
    db1=connect_redis(1)
    tasks=[]
    for inner_key in db1.keys():
        if inner_key[:len(user_id)]==user_id:
            title=inner_key[len(user_id):]
            val=db1.get(inner_key)
            y,mo,d,h,mi=token_to_datetime(val)
            deadline=dt(y,mo,d,h,mi)
            if fil(deadline):
                tasks.append((deadline,title,val))
    tasks.sort()
    return [tasks[i][1:] for i in range(len(tasks))]