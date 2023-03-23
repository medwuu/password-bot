# -*- coding: utf-8 -*-
import sqlite3

connect = sqlite3.connect("database.db", check_same_thread=False)
cursor = connect.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS manager(
id INT,
source TEXT,
login TEXT,
password TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS phrases(
id INTEGER UNIQUE,
phrase TEXT,
message_id INTEGER DEFAULT ''
)""")

def checkForPhrase(id):
    return cursor.execute(f"""SELECT phrase FROM phrases WHERE id = '{id}'""").fetchone()

def addPhrase(id, phrase):
    cursor.execute(f"""INSERT INTO phrases(id, phrase) VALUES
                   ('{id}', '{phrase}')""")
    connect.commit()
    return "Успех"


# TODO проверка на существование записи
def addPasswordList(id, password_list):
    for line in password_list:
        cursor.execute(f"""INSERT INTO manager (
            id, source, login, password) VALUES(
            '{id}', '{line[0]}', '{line[1]}', '{line[2]}'
            )""")
    connect.commit()

def getPasswords(id):
    return cursor.execute(f"""SELECT source, login, password FROM manager WHERE id = '{id}'""").fetchall()

def addMessageID(id, message_id):
    cursor.execute(f"""UPDATE phrases SET message_id = '{message_id}' WHERE id = '{id}'""")
    connect.commit()

def readMessageID(id):
    return cursor.execute(f"""SELECT message_id FROM phrases WHERE id = '{id}'""").fetchone()[0]

def deleteMessageID(id):
    cursor.execute(f"""UPDATE phrases SET message_id = '' WHERE id = '{id}'""")
    connect.commit()

def changeDBPhrase(id, new_phrase):
    cursor.execute(f"""UPDATE phrases SET phrase = '{new_phrase}' WHERE id = '{id}'""")
    connect.commit()
    return "Успех!"

def deleteDBPasswords(id):
    cursor.execute(f"""DELETE FROM manager WHERE id = '{id}'""")
    connect.commit()
    return "Все пароли успешно удалены!"