#!/usr/bin/env python3

import os
import sys
from ai_storage import storage
from telegram import ParseMode, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, run_async, CommandHandler, ConversationHandler, MessageHandler, Filters

s = storage()
 
@run_async
def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Kaboom!")


@run_async
def pulse(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Kaboom!")

@run_async
def info(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Kaboom!")

@run_async
def custom_question(update, context):
    data = s.show_all()
    values = list(data.values())
    length = len(values)

    if length == 0:
        answer = "Found 0 notes"
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=answer,
                                 parse_mode=ParseMode.MARKDOWN)

    else:
        answer = "Found *{}* notes:\n\n".format(length)
        for i in range(length):
            answer += "{}.\t_{}_\n{}\n\n".format(i + 1, values[i]["timestamp"], values[i]["text"])

        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=answer,
                                 parse_mode=ParseMode.MARKDOWN)


def add_name(update, context):

    keyboard = [
        [KeyboardButton("Miss", callback_data="miss"),
         KeyboardButton("Cancel", callback_data="cancel")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    update.message.reply_text(
        "Enter topic",
        reply_markup=reply_markup
    )

    return _ADD_NAME


def add_text(update, context):
    if update.message.text == 'cancel':
        return ConversationHandler.END

    buf["name"] = update.message.text
    context.bot.send_message(chat_id=update.message.chat_id, text='Enter text')
    return _ADD_TEXT


def add_date(update, context):
    buf["text"] = update.message.text
    context.bot.send_message(chat_id=update.message.chat_id, text='Enter date')
    return _ADD_DATE


def add_media(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Attach media')
    return _ADD_MEDIA


def add_success(update, context):
    id = s.add(buf["name"], buf["text"])
    name = s.get(id)["name"]
    text = s.get(id)["text"]

    context.bot.send_message(chat_id=update.message.chat_id, text='Success!')

    context.bot.send_message(chat_id=update.message.chat_id,
                             text="_{}_\n\n*{}*\n\n{}".format(id, name, text),
                             parse_mode=ParseMode.MARKDOWN)

    return ConversationHandler.END

def add_cancel(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='cancel')
    return ConversationHandler.END


_ADD_NAME, _ADD_TEXT, _ADD_DATE, _ADD_MEDIA = range(4)

if __name__ == '__main__':

    telegram_api_token = os.environ.get('TELEGRAM_API_TOKEN')

    if telegram_api_token is None:
        sys.exit(0x01)

    updater = Updater(telegram_api_token, use_context=True)

    add_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_name)],

        states={
            _ADD_NAME: [MessageHandler(Filters.text, add_text)],
            _ADD_TEXT: [MessageHandler(Filters.text, add_date)],
            _ADD_DATE: [MessageHandler(Filters.text, add_media)],
            _ADD_MEDIA: [MessageHandler(Filters.text, add_success)]
        },

        fallbacks=[MessageHandler(Filters.regex('^cancel'), add_cancel)]
    )

    updater.dispatcher.add_handler(add_conversation_handler)

    updater.dispatcher.add_handler(CommandHandler('pulse', pulse))

    updater.start_polling()
    updater.idle()
