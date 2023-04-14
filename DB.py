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

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
id INTEGER UNIQUE,
phrase TEXT,
message_id INT DEFAULT '',
in_manager INT DEFAULT 0
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS chat(
id INT UNIQUE,
connected_with INT DEFAULT 0
)""")

def checkForPhrase(id):
    return cursor.execute(f"""SELECT phrase FROM users WHERE id = '{id}'""").fetchone()

def addPhrase(id, phrase):
    cursor.execute(f"""INSERT INTO users(id, phrase) VALUES
                   ('{id}', '{phrase}')""")
    connect.commit()
    return "Успех"

def checkInManager(id):
    return cursor.execute(f"""SELECT in_manager FROM users WHERE id = '{id}'""").fetchone()[0]

def editInManager(id, value=0):
    cursor.execute(f"""UPDATE users SET in_manager = '{value}' WHERE id = '{id}'""")
    connect.commit()

def addPassword(id, pass_element):
    if not tuple(x for x in pass_element) in getPasswords(id):
        cursor.execute(f"""INSERT INTO manager (
            id, source, login, password) VALUES(
            '{id}', '{pass_element[0]}', '{pass_element[1]}', '{pass_element[2]}'
            )""")
        connect.commit()

def getPasswords(id):
    return cursor.execute(f"""SELECT source, login, password FROM manager WHERE id = '{id}'""").fetchall()

def addMessageID(id, message_id):
    cursor.execute(f"""UPDATE users SET message_id = '{message_id}' WHERE id = '{id}'""")
    connect.commit()

def readMessageID(id):
    return cursor.execute(f"""SELECT message_id FROM users WHERE id = '{id}'""").fetchone()[0]

def deleteMessageID(id):
    cursor.execute(f"""UPDATE users SET message_id = '' WHERE id = '{id}'""")
    connect.commit()

def changeDBPhrase(id, new_phrase):
    cursor.execute(f"""UPDATE users SET phrase = '{new_phrase}' WHERE id = '{id}'""")
    connect.commit()
    return "Успех!"

def deleteSinglePassword(id, line_to_delete):
    cursor.execute(f"""DELETE FROM manager WHERE id = '{id}' AND
    source = '{line_to_delete[0]}' AND
    login = '{line_to_delete[1]}' AND
    password = '{line_to_delete[2]}'""")
    connect.commit()
    return "Успех!"

def deleteAllPasswords(id):
    cursor.execute(f"""DELETE FROM manager WHERE id = '{id}'""")
    connect.commit()
    return "Все пароли успешно удалены!"

def burnAllDB(id):
    deleteAllPasswords(id)
    cursor.execute(f"""DELETE FROM users WHERE id = '{id}'""")
    connect.commit()
    return "Всё удалено!"



def addToQueue(id):
    first = checkForAlone()
    if first:
        cursor.execute(f"""UPDATE chat SET connected_with = '{id}' WHERE id = '{first[0]}'""")
        cursor.execute(f"""INSERT INTO chat(id, connected_with) VALUES(
        '{id}',
        '{first[0]}'
        )""")
        connect.commit()
        return "Собеседник найден!"
    else:
        cursor.execute(f"""INSERT INTO chat(id) VALUES('{id}')""")
        connect.commit()
        return "Вы встали в очередь"

def checkForAlone():
    return cursor.execute(f"""SELECT id FROM chat WHERE connected_with = '0'""").fetchone()

def connectedPersons(id):
    return cursor.execute(f"""SELECT connected_with FROM chat WHERE id = '{id}'""").fetchone()

def deleteFromQueue(id):
    cursor.execute(f"""DELETE FROM chat WHERE id = '{id}'""")
    connect.commit()
    return "Вы покинули чат"