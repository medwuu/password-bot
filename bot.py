# -*- coding: utf-8 -*-
import config
import DB

import logging
import time
import json
import os
import csv

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
        menu(message)


# TODO main menu
@bot.message_handler(commands=['menu'])
def menu(message):
    logging.info("Triggered menu()")
    DB.editInManager(message.from_user.id)
    start_deleting = DB.readMessageID(message.from_user.id)
    if start_deleting:
        finish_deleting = bot.send_message(message.chat.id, "Что вас интересует?").id
        logging.info(f"Started deleting process ({int(start_deleting)}/{finish_deleting})")
        for message_to_delete in range(int(start_deleting), finish_deleting):
            bot.delete_message(message.chat.id, message_to_delete)
            logging.info(f"Deleted message #{message_to_delete}")
        DB.deleteMessageID(message.from_user.id)
    else:
        bot.send_message(message.chat.id, "Что вас интересует?")




@bot.message_handler(content_types=['text'])
def text(message):
    logging.info("Triggered text()")
    if message.text == DB.checkForPhrase(message.from_user.id)[0]:
        managerMenu(message)
    if DB.checkInManager(message.from_user.id):
        if message.text == "Изменение паролей":
            markup = types.ReplyKeyboardMarkup(True, row_width=3)
            file_import = types.KeyboardButton("Импорт из файла")
            just_add = types.KeyboardButton("Добавить один пароль")
            just_delete = types.KeyboardButton("Удалить один пароль")
            markup.add(file_import, just_add, just_delete)
            bot_msg = bot.send_message(message.chat.id, "Выберите режим", markup=markup)
            bot.register_next_step_handler(bot_msg, editPasswords)
        elif message.text == "Посмотреть пароли":
            showPasswords(message)
        elif message.text == "Удалить все пароли":
            deletePasswords(message)
        elif message.text == "Изменить фразу":
            bot_msg = bot.send_message(message.chat.id, "Пришлите вашу новую фразу")
            bot.register_next_step_handler(bot_msg, changePhrase)
        elif message.text == "Выход":
            menu(message)
    else:
        bot.send_message(message.chat.id, "Извините, не понял вас :с")
        menu(message)



def managerMenu(message):
    logging.info("Triggered managerMenu()")
    DB.editInManager(message.from_user.id, 1)
    DB.addMessageID(message.from_user.id, message.id)
    markup = types.ReplyKeyboardMarkup(True, row_width=3)
    import_json = types.KeyboardButton("Изменение паролей")
    show_passwords = types.KeyboardButton("Посмотреть пароли")
    delete_all = types.KeyboardButton("Удалить все пароли")
    change_phrase = types.KeyboardButton("Изменить фразу")
    exit = types.KeyboardButton("Выход")
    markup.add(import_json, show_passwords, delete_all, change_phrase, exit)
    bot.send_message(message.chat.id, "Меню менеджера паролей. Что вас интересует?", reply_markup=markup)
    




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

def editPasswords(message):
    logging.info("Triggered editPasswords()")
    if message.text == "Импорт из файла":
        bot_msg = bot.send_message(message.chat.id, "Пришлите, пожалуйста, ваш JSON или CSV файл")
        bot.register_next_step_handler(bot_msg, documentHandler)
    # TODO
    elif message.text == "Добавить один пароль":
        bot.send_message(message.chat.id, "В разработке...")
        menu(message)
    # TODO
    elif message.text == "Удалить один пароль":
        bot.send_message(message.chat.id, "В разработке...")
        menu(message)
    else:
        bot.send_message(message.chat.id, "Извините, не понял вас :с")
        menu(message)


def documentHandler(message):
    logging.info("Triggered getJson()")
    try:
        extension = message.document.file_name.split(".")[-1]
    except AttributeError:
        extension = None
    if extension in ["json", "csv"]:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f"files/{message.document.file_name}"
        with open(src, "wb") as file:
            file.write(downloaded_file)
            logging.info(f"Created file {src.split('/')[1]}")
        jsonProcess(message, src) if extension == "json" else csvProcess(message, src)
    else:
        bot.send_message(message.chat.id, "Я принимаю только файлы JSON")
        menu(message)

def jsonProcess(message, file_src):
    logging.info("Triggered jsonProcess()")
    with open(file_src, "r") as file:
        passwords_list = json.load(file)["passwords"]
    logging.info("Triggered DB.addPassword()")
    for pass_element in passwords_list:
        DB.addPassword(message.from_user.id, pass_element)
    bot.send_message(message.chat.id, "Пароли успешно добавлены!")
    os.remove(file_src)
    logging.info("File succesfully deleted")
    menu(message)

def csvProcess(message, file_src):
    logging.info("Triggered csvProcess()")
    with open(file_src) as csv_file:
        reader = csv.reader(csv_file)
        for pass_element in reader:
            DB.addPassword(message.from_user.id, pass_element[:3])
    bot.send_message(message.chat.id, "Пароли успешно добавлены!")
    os.remove(file_src)
    logging.info("File succesfully deleted")
    menu(message)

def showPasswords(message):
    logging.info("Triggered showPasswords()")
    passwords_list = DB.getPasswords(message.from_user.id)
    if not passwords_list:
        bot.send_message(message.chat.id, "У вас пока нет добавленных паролей")
        menu(message)
    else:
        for password_num, password_line in enumerate(passwords_list, start=1):
            bot.send_message(message.chat.id, f"{password_num}. Источник: <code>{password_line[0]}</code>\n" +
                             f"логин: <code>{password_line[1]}</code>\n" +
                             f"пароль: <code>{password_line[2]}</code>",
                             parse_mode="html")

def changePhrase(message):
    new_phrase = message.text
    answer = DB.changeDBPhrase(message.from_user.id, new_phrase)
    bot.send_message(message.chat.id, answer)
    time.sleep(5)
    menu(message)

def deletePasswords(message):
    answer = DB.deleteAllPasswords(message.from_user.id)
    bot.send_message(message.chat.id, answer)
    menu(message)
    
    
    


def start():
    logging.basicConfig(level=logging.INFO, filename="logging.log", filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Succesfull import")
    try:
        logging.info("Succesfull launch")
        bot.polling()
    except Exception as error:
        logging.critical(f"Launch failed! Error:\n{error}", exc_info=True)


start()