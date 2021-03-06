from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import *
from linebot.models import *

import os
import psycopg2
import json

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['LINE_BOT_TOKEN'])
handler = WebhookHandler(os.environ['LINE_BOT_SECRET'])

db_url = os.environ['DATABASE_URL']

# init

rich_menu_ids = {}
rich_menu_ids['main'] = line_bot_api.create_rich_menu(
    rich_menu=RichMenu(
        size=RichMenuSize(width=1200, height=600),
        selected=False,
        name="main",
        chat_bar_text="Tap here",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=0,
                    y=0,
                    width=540,
                    height=600
                ),
                action=MessageAction(
                    text="即時狀態查詢"
                )
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=660,
                    y=0,
                    width=540,
                    height=600
                ),
                action=MessageAction(
                    text="登錄機器狀態"
                )
            )
        ]
    )
)
with open("img/rich_menu/main.png", 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_ids['main'], 'image/png', f)
line_bot_api.set_default_rich_menu(rich_menu_ids['main'])


@app.route("/")
def root():
    return 'OK'


@app.route("/callback", methods=["POST"])
def callback():
    sign = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, sign)
    except InvalidSignatureError:
        print("Invalid sinature, check access token.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def textmessage(event):

    mesg = event.message.text.split(' ')

    if mesg[0] == "ping" or mesg[0] == "Ping":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="PONG!"
            )
        )
    if mesg[0] == "即時狀態查詢":
        with psycopg2.connect(db_url, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT status FROM machine_status;')
                rec = json.loads(cur.fetchone()[0])
                reply_text = ""
                for machine in rec:
                    reply_text += machine['name'] + \
                        "：" + machine['status'] + "\n"

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        reply_text.strip()
                    )
                )
    if mesg[0] == "登錄機器狀態":
        quick_reply_buttons = []
        with psycopg2.connect(db_url, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT status FROM machine_status;')
                rec = json.loads(cur.fetchone()[0])
                for machine in rec:
                    quick_reply_buttons.append(
                        QuickReplyButton(
                            action=MessageAction(
                                label=machine['name'],
                                text="狀態 " + machine['name']
                            )
                        )
                    )
        quick_reply_buttons.append(
            QuickReplyButton(
                action=MessageAction(
                    label="取消",
                    text="取消"
                )
            )
        )

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="請選擇機器",
                quick_reply=QuickReply(
                    items=quick_reply_buttons
                )
            )
        )
    if mesg[0] == "狀態":
        with psycopg2.connect(db_url, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT status FROM machine_status;')
                rec = json.loads(cur.fetchone()[0])
                for machine in rec:
                    if machine['name'] == mesg[1]:
                        if len(mesg) == 2:
                            reply_text = "{}：{}".format(
                                machine['name'], machine['status'])
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(
                                    text=reply_text,
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(
                                                action=MessageAction(
                                                    label="使用中",
                                                    text="狀態 {machine_name} 使用中".format(
                                                        machine_name=machine['name'])
                                                )
                                            ),
                                            QuickReplyButton(
                                                action=MessageAction(
                                                    label="閒置",
                                                    text="狀態 {machine_name} 閒置".format(
                                                        machine_name=machine['name'])
                                                )
                                            ),
                                            QuickReplyButton(
                                                action=MessageAction(
                                                    label="取消",
                                                    text="取消"
                                                )
                                            )
                                        ]
                                    )
                                )
                            )
                        if len(mesg) == 3:
                            if mesg[2] in ['使用中', '閒置']:
                                machine['status'] = mesg[2]
                                cur.execute('update machine_status set status = \'{status}\' where floor = 9;'.format(
                                    status=json.dumps(rec)))
                                reply_text = "{}：{}".format(
                                    machine['name'], machine['status'])
                                line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage(
                                        text=reply_text,
                                    )
                                )


if __name__ == "__main__":
    app.run()
