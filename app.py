from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import *
from linebot.models import *

import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['LINE_BOT_TOKEN'])
handler = WebhookHandler('LINE_BOT_SECRET')

@app.route("/")
def root():
    return 'OK'

@app.route("/callback", methods = ["POST"])
def callback():
    sign = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, sign)
    except InvalidSignatureError:
        print("Invalid sinature, check access token.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message = TextMessage)
def textmessage(event):
    if event.message.text == "ping" or event.message.text == "Ping":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="PONG!"
            )
        )

if __name__ == "__main__":
    app.run()
