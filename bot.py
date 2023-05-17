import telebot

import secrets
from secrets import BOT_TOKEN
import os

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def greetings(message):
    bot.reply_to(message, 'To grab and parse messages type /parse\nTo watch summarized info type /sum')


@bot.message_handler(commands=['link'])
def set_link(message):
    msg = bot.reply_to(message, 'Введите ссылку на чат: ')
    bot.register_next_step_handler(msg, after_text)

def after_text(message):
    link = message.text
    r = open("link.txt", "w", encoding='utf8')
    r.write(link)
    r.close()

@bot.message_handler(commands=['sum'])
def send_results(message):
    os.system("./main.py")
    with open("text.txt") as f:
        text = f.readlines().pop(0)
    with open("result.txt") as f:
        summary_text = f.read()
    bot.reply_to(message, summary_text)


bot.infinity_polling()


'''
@bot.message_handler(commands=['sum'])
def send_sum(message):
    bot.reply_to(message, 'summarizer response will be here')

bot.infinity_polling()
'''
