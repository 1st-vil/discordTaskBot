import os
from os.path import join,dirname
from dotenv import load_dotenv

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

notice_time=[
    '07:10',
    '14:50',
    '19:00',
]