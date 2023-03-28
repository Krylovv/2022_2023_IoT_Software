import telebot
from secrets import BOT_TOKEN
import os

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def greetings(message):
    bot.reply_to(message, 'To grab and parse messages type /parse\nTo watch summarized info type /sum')


@bot.message_handler(commands=['parse'])
def send_results(message):
    os.system("./main.py")
    with open("text.txt") as f:
        text = f.readlines().pop(0)
    bot.reply_to(message, 'Done parsing!')

@bot.message_handler(commands=['sum'])
def send_sum(message):
    bot.reply_to(message, 'summarizer response will be here')

bot.infinity_polling()
