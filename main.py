#!/usr/bin/env python3

import os
import sys
import json
import random
from ai_storage.storage import Storage
from telegram import ParseMode, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, run_async, CommandHandler, ConversationHandler, MessageHandler, Filters

s = Storage('data/data.json', 'data/tayga_upos_skipgram_300_2_2019/model.bin')

_stories = json.loads(open("data/stories.json", 'r').read())["data"]
_events = "".join(json.loads(open("data/events.json", 'r').read())["data"])
_info = json.loads(open("data/info.json", 'r').read())

@run_async
def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Здравствуйте!\n" + \
                                  "Меня зовут Петр, я бот приемной комиссии НИУ МФТИ. Здесь можно найти ответы на интересующие " + \
                                  "Вас *вопросы* о поступлении, введя команду /info, или же можно просто *спросить* меня, а я попытаюсь ответить :)\n\n" + \
                                  "Все возможности бота доступны по коменде /help",
                             parse_mode=ParseMode.MARKDOWN)

@run_async
def info(update, context):

    info_keys = list(_info.keys())

    keyboard = [[KeyboardButton(info_keys[0], callback_data=info_keys[0])],
                [KeyboardButton(info_keys[1], callback_data=info_keys[1])],
                [KeyboardButton(info_keys[2], callback_data=info_keys[2])],
                [KeyboardButton(info_keys[3], callback_data=info_keys[3])],
                [KeyboardButton(info_keys[4], callback_data=info_keys[4])],
                [KeyboardButton(info_keys[5], callback_data=info_keys[5])],
                [KeyboardButton(info_keys[6], callback_data=info_keys[6])],
                [KeyboardButton(info_keys[7], callback_data=info_keys[7])],
                [KeyboardButton("Отмена", callback_data="Отмена")]]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    update.message.reply_text(
        "Выберите, что Вас интересует:",
        reply_markup=reply_markup
    )

    return 1

@run_async
def show_info(update, context):
    if update.message.text == 'Отмена':
        return ConversationHandler.END

    answer = _info[update.message.text]

    context.bot.send_message(chat_id=update.message.chat_id,
                             text=answer,
                             parse_mode=ParseMode.MARKDOWN)

    return ConversationHandler.END

@run_async
def contacts(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="*График работы* приёмной комиссии летом 2020 года по приёму документов для поступающих на 1 курс " + \
                                  "бакалавриата и специалитета будет опубликован не позднее 01 июня 2020 года.\n\n" + \
                                  "*Время работы (вне приемной кампании)*: с понедельника по пятницу, с 9:00 до 18:00, обед с 12:00 до 13:00\n" + \
                                  "*Телефон*: +7 (495) 408-48-00\n" + \
                                  "*E-mail*: [pk@mipt.ru](pk@mipt.ru)",
                             parse_mode=ParseMode.MARKDOWN)

@run_async
def help(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="/info - Ответы на часто задаваемые *вопросы*\n" + \
                             "/events - Важные события и *график работы* приемной комиссии\n" + \
                             "/contacts - Контакты приемной комиссии\n" + \
                             "/random - Случайная физтеховская байка\n\n" + \
                             "Также я могу ответить на многие другие вопросы о поступлении - просто спросите:)",
                             parse_mode=ParseMode.MARKDOWN)

@run_async
def events(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=_events,
                             parse_mode=ParseMode.MARKDOWN)

@run_async
def story(update, context):
    story_list = list(_stories.values())
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=story_list[random.randint(0,len(story_list)-1)],
                             parse_mode=ParseMode.MARKDOWN)

@run_async
def custom_text_question(update, context):
    question = update.message.text
    answer = s.search(question)[0]
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=answer,
                             parse_mode=ParseMode.MARKDOWN)

if __name__ == '__main__':

    telegram_api_token = os.environ.get('TELEGRAM_API_TOKEN')

    if telegram_api_token is None:
        sys.exit(0x01)

    updater = Updater(telegram_api_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('info', info))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('contacts', contacts))
    updater.dispatcher.add_handler(CommandHandler('events', events))
    updater.dispatcher.add_handler(CommandHandler('random', story))
    updater.dispatcher.add_handler(MessageHandler(Filters.text and Filters.regex('^(?!.*Отмена)'), custom_text_question))

    updater.start_polling()
    updater.idle()
