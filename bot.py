# -*- coding: utf-8 -*-
import config
import DB

import logging
import time

import telebot

from telebot import types

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    id = message.from_user.id
    if not DB.checkForPhrase(id):
        logging.info("Triggered welcome()")
        bot_msg = bot.send_message(message.chat.id, "Придумайте контрольное слово/фразу. Старайтесь не придумывать лёгое слово/фразу")
        bot.register_next_step_handler(bot_msg, addPhrase, id)
    else:
        menu()




# TODO main menu
@bot.message_handler(commands=['menu'])
def menu():
    logging.info("Triggered menu()")




# TODO manager menu
def managerMenu(message):
    pass




# additional functions
def addPhrase(message, id):
    logging.info(f"Triggered addPhrase(). Args: phrase='{message.text}', id='{id}'")
    answer = DB.addPhrase(id, message.text)
    bot_msg = bot.send_message(id, answer)
    logging.info("Phrase added to DB")
    time.sleep(5)
    for message_id in range(message.id - 1, bot_msg.id + 1):
        bot.delete_message(id, message_id)
        logging.info(f"Deleted welcome() message #{message_id}")
    


def start():
    logging.basicConfig(level=logging.INFO, filename="logging.log", filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Succesfull import")
    try:
        logging.info("Succesfull launch")
        bot.polling()
    except Exception as error:
        logging.critical(f"Launch failed! Error:\n{error}", exc_info=True)