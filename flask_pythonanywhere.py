# -*- coding: utf-8 -*-
import config
import telebot
from flask import Flask, request, abort
import logging
import nsubot

bot = nsubot.bot

logger = telebot.logger.setLevel(logging.WARN)

WEBHOOK_URL = "https://MilQ.pythonanywhere.com/{}".format(config.webhook_guid)

app = Flask(__name__)


@app.route('/{}'.format(config.webhook_guid), methods=['POST'])
def index():
    update = request.json
    if update:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
        return '', 200
    else:
        abort(403)


bot.remove_webhook()

# Ставим заново вебхук
bot.set_webhook(url=WEBHOOK_URL)
