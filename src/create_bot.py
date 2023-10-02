from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from data.bot_token import TOKEN

bot = TeleBot(TOKEN)

menu_keyboard = ReplyKeyboardMarkup(True, False)
button1 = KeyboardButton('1 месяц')
button2 = KeyboardButton('3 месяца')
button3 = KeyboardButton('Все время')
menu_keyboard.row(button1, button2, button3)

