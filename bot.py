# -*- coding: utf-8 -*-
import config
import DB

import logging

import telebot

from telebot import types

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    id = message.from_user.id
    if not DB.checkForPhrase(id):
        logging.info("Triggered welcome()")
        bot_msg = bot.send_message(message.chat.id, "Придумайте контрольное слово/фразу")
        bot.register_next_step_handler(bot_msg, addPhrase, id)
    else:
        menu()





@bot.message_handler(commands=['menu'])
def menu():
    logging.info("Triggered menu()")



def addPhrase(message, id):
    logging.info(f"Triggered addPhrase(). Args: phrase='{message.text}', id='{id}'")
    answer = DB.addPhrase(id, message.text)
    bot.send_message(id, answer)
    logging.info("Phrase added to DB")
    



def start():
    logging.basicConfig(level=logging.INFO, filename="logging.log", filemode="w", format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Import succesfull")
    try:
        logging.info("Succesfull launch!")
        bot.polling()
    except Exception as error:
        logging.critical(f"Launch failed! Error:\n{error}", exc_info=True)