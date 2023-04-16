# -*- coding: utf-8 -*-
import config
import DB

import csv
import json
import logging
import os
import time

from telebot import TeleBot, types

bot = TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    id = message.from_user.id
    if not DB.checkForPhrase(id):
        logging.info("Triggered welcome()")
        bot_msg = bot.send_message(message.chat.id, "Вас приветствует секрутный менеджер паролей!\nПридумайте контрольное слово/фразу. Старайтесь не придумывать лёгое слово/фразу")
        bot.register_next_step_handler(bot_msg, addPhrase, id)
    else:
        menu(message)



@bot.message_handler(commands=['menu'])
def menu(message):
    logging.info("Triggered menu()")
    DB.editInManager(message.from_user.id)
    start_deleting = DB.readMessageID(message.from_user.id)
    if start_deleting:
        finish_deleting = bot.send_message(message.chat.id, "Что вас интересует?").id
        time.sleep(3)
        logging.info(f"Started deleting process ({int(start_deleting)}/{finish_deleting})")
        for message_to_delete in range(int(start_deleting), finish_deleting):
            bot.delete_message(message.chat.id, message_to_delete)
            logging.info(f"Deleted message #{message_to_delete}")
        DB.deleteMessageID(message.from_user.id)

    markup = types.ReplyKeyboardMarkup(True, row_width=3)
    search = types.KeyboardButton("Поиск собеседника")
    markup.add(search)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}🤙🏻! Добро пожаловать в анонимный чат👀! Нажми на поиск собеседника.', reply_markup= markup)


@bot.message_handler(content_types=['text'])
def text(message):
    logging.info("Triggered text()")
    if message.text == DB.checkForPhrase(message.from_user.id)[0]:
        managerMenu(message)
    elif DB.checkInManager(message.from_user.id):
        if message.text == "Изменение паролей":
            markup = types.ReplyKeyboardMarkup(True, row_width=3)
            file_import = types.KeyboardButton("Импорт из файла")
            just_add = types.KeyboardButton("Добавить один пароль")
            just_delete = types.KeyboardButton("Удалить один пароль")
            markup.add(file_import, just_add, just_delete)
            bot_msg = bot.send_message(message.chat.id, "Выберите режим", reply_markup=markup)
            bot.register_next_step_handler(bot_msg, editPasswords)
        elif message.text == "Посмотреть пароли":
            showPasswords(message)
        elif message.text == "Удалить все пароли 🔥":
            deletePasswords(message)
        elif message.text == "Изменить фразу":
            bot_msg = bot.send_message(message.chat.id, "Пришлите вашу новую фразу")
            bot.register_next_step_handler(bot_msg, changePhrase)
        elif message.text == "Удалить следы присутствия":
            burnAll(message)
        elif message.text == "Выход":
            menu(message)
    # chat functions
    elif message.text == "Поиск собеседника":
        searchChat(message)
    elif message.text == "Покинуть чат" and DB.connectedPersons(message.from_user.id):
        stopChat(message)
    elif DB.connectedPersons(message.from_user.id):
        bot.send_message(DB.connectedPersons(message.from_user.id)[0], message.text)
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
    delete_all = types.KeyboardButton("Удалить все пароли 🔥")
    change_phrase = types.KeyboardButton("Изменить фразу")
    burn = types.KeyboardButton("Удалить следы присутствия")
    exit = types.KeyboardButton("Выход")
    markup.add(import_json, show_passwords, delete_all, change_phrase, burn, exit)
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
    menu(message)

def editPasswords(message):
    logging.info("Triggered editPasswords()")
    if message.text == "Импорт из файла":
        bot_msg = bot.send_message(message.chat.id, "Пришлите, пожалуйста, ваш JSON или CSV файл")
        bot.register_next_step_handler(bot_msg, documentHandler)
    elif message.text == "Добавить один пароль":
        bot_msg = bot.send_message(message.chat.id, "Пароль от какого сайта/приложения вы хотите добавить?")
        bot.register_next_step_handler(bot_msg, askForSource)
    elif message.text == "Удалить один пароль":
        showPasswords(message)
        bot_msg = bot.send_message(message.chat.id, "Введите номер пароля, который необходимо удалить")
        bot.register_next_step_handler(bot_msg, deleteOnePassword)
    else:
        bot.send_message(message.chat.id, "Извините, не понял вас :с")
        menu(message)

def documentHandler(message):
    logging.info("Triggered documentHandler()")
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
        for index, pass_element in enumerate(reader):
            if index != 0:
                DB.addPassword(message.from_user.id, pass_element[:3])
    bot.send_message(message.chat.id, "Пароли успешно добавлены!")
    os.remove(file_src)
    logging.info("File succesfully deleted")
    menu(message)

def askForSource(message):
    logging.info("Triggered askForSource()")
    source = message.text
    bot_msg = bot.send_message(message.chat.id, f"Отлично! Теперь введите логин от {source}")
    bot.register_next_step_handler(bot_msg, askForLogin, source)

def askForLogin(message, source):
    logging.info("Triggered askForLogin()")
    login = message.text
    bot_msg = bot.send_message(message.chat.id, f"И последнее. Введите пароль от {source}")
    bot.register_next_step_handler(bot_msg, askForPassword, source, login)

def askForPassword(message, source, login):
    logging.info("Triggered askForPassword()")
    password = message.text
    logging.info("Triggered DB.addPassword()")
    DB.addPassword(message.from_user.id, [source, login, password])
    bot.send_message(message.chat.id, "Пароль успешно добавлен!")
    menu(message)

def deleteOnePassword(message):
    logging.info("Triggered deleteOnePassword()")
    required_number = int(message.text)
    passwords_list = DB.getPasswords(message.from_user.id)
    if 0 < required_number < len(passwords_list) + 1:
        line_to_delete = passwords_list[required_number - 1]
        logging.info("Triggered DB.deleteSinglePassword()")
        bot.send_message(message.chat.id, DB.deleteSinglePassword(message.from_user.id, line_to_delete))
        menu(message)
    else:
        bot.send_message(message.chat.id, "Неправильное число")
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

def burnAll(message):
    logging.info("Triggered burnAll()")
    menu(message)
    bot_msg = bot.send_message(message.chat.id, DB.burnAllDB(message.from_user.id))
    time.sleep(2)
    bot.delete_message(message.chat.id, bot_msg.id)


# chat functions
def searchChat(message):
    logging.info("Triggered searchChat")
    markup = types.ReplyKeyboardMarkup(True, row_width=3)
    leave = types.KeyboardButton("Покинуть чат")
    markup.add(leave)
    answer = DB.addToQueue(message.from_user.id)
    if answer == "Собеседник найден!":
        bot.send_message(*DB.connectedPersons(message.from_user.id), answer)
    bot.send_message(message.chat.id, answer, reply_markup=markup)

def stopChat(message):
    try:
        logging.info("stopChat(): user 2 left chat")
        second = DB.connectedPersons(message.from_user.id)[0]
        DB.deleteFromQueue(second)
        bot.send_message(second, "Собеседник покинул чат")
    except TypeError:
        logging.info("stopChat(): user 1 left chat")
        bot.send_message(message.chat.id, DB.deleteFromQueue(message.from_user.id))
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