from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import *
from linebot.models import *

import os
import psycopg2

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
                cur.execute('SELECT * FROM machine_status;')
                line_bot_api.reply_message(
                    event.reply_token,
                    str(cur.fetchone())
                )


if __name__ == "__main__":
    app.run()
