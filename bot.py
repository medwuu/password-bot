import config
import telebot
from telebot import types

bot = telebot.TeleBot(config.TOKEN)







def start():
    bot.polling()