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

    mesg = event.message.text

    if mesg == "ping" or mesg == "Ping":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="PONG!"
            )
        )
    if mesg == "即時狀態查詢":
        with psycopg2.connect(db_url, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT status FROM machine_status;')
                rec = json.loads(cur.fetchone())
                for machine, status in rec.items():
                    reply_text += machine + "：" + status + "\n"
                
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        reply_text
                    )
                )


if __name__ == "__main__":
    app.run()
