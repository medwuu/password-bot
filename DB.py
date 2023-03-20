# -*- coding: utf-8 -*-
import sqlite3

connect = sqlite3.connect("database.db", check_same_thread=False)
cursor = connect.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS manager(
id INT,
login TEXT,
password TEXT,
source TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS phrases(
id INTEGER UNIQUE,
phrase TEXT
)""")

def checkForPhrase(id):
    return cursor.execute(f"""SELECT * FROM phrases WHERE id = '{id}'""").fetchone()

def addPhrase(id, phrase):
    cursor.execute(f"""INSERT INTO phrases(id, phrase) VALUES
                   ('{id}', '{phrase}')""")
    connect.commit()
    return "Успех"