#!/usr/bin/env python3

import os
import sys
from ai_storage.storage import storage
from telegram import ParseMode, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, run_async, CommandHandler, ConversationHandler, MessageHandler, Filters

#s = storage("data/data.json")

@run_async
def start(update, context):
    print('hey1')
    context.bot.send_message(chat_id=update.message.chat_id, text="Kaboom!")

@run_async
def pulse(update, context):
    print('hey2')
    context.bot.send_message(chat_id=update.message.chat_id, text="Kaboom!")

@run_async
def info(update, context):
    print('hey3')
    context.bot.send_message(chat_id=update.message.chat_id, text="Kaboom!")

@run_async
def custom_question(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Kaboom!")

if __name__ == '__main__':

    telegram_api_token = os.environ.get('TELEGRAM_API_TOKEN')

    if telegram_api_token is None:
        sys.exit(0x01)

    updater = Updater(telegram_api_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('pulse', pulse))
    updater.dispatcher.add_handler(CommandHandler('info', info))

    updater.start_polling()
    updater.idle()
