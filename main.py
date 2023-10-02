from datetime import datetime, timedelta
from telebot.types import Message
from src.create_bot import bot, menu_keyboard
import pandas as pd
import matplotlib
import io
from PIL import Image
matplotlib.use('agg')
import matplotlib.pyplot as plt


@bot.message_handler(commands=['start'])
def start_message(message: Message):
    msg = bot.send_message(message.chat.id, 'Привет. Вводи свой вес, а я буду сохранять твою историю взвешиваний и '
                                            'смогу показать тебе график.', reply_markup=menu_keyboard)
    bot.register_next_step_handler(msg, menu)


@bot.message_handler(content_types=['text'])
def menu(message: Message):
    if message.text in ('1 месяц', '3 месяца', 'Все время'):
        image = plot_history(period=message.text, user_id=message.from_user.id)
        action = bot.send_photo(message.chat.id, image)
        bot.register_next_step_handler(action, menu)
    else:
        try:
            weight = float(message.text.replace(',', '.'))
            add_weight(weight=weight, user_id=message.from_user.id)
            msg = bot.send_message(message.chat.id, 'Записал. Если ошибся, просто напиши еще раз',
                                   reply_markup=menu_keyboard)
            bot.register_next_step_handler(msg, menu)
        except:
            msg = bot.send_message(message.chat.id, 'Точно правильный формат? Напиши еще раз',
                                   reply_markup=menu_keyboard)
            bot.register_next_step_handler(msg, menu)


def add_weight(weight, user_id):
    today = datetime.today().strftime('%d.%m.%Y')
    new_weight = pd.DataFrame({'create_dt': [today],
                               'user_id': [user_id],
                               'weight': [weight]
                               })
    path_to_csv = 'data/data.csv'
    data = pd.read_csv(path_to_csv)
    if today in data[data.user_id == user_id].values:
        data.loc[(data.user_id == user_id) & (data.create_dt == today), 'weight'] = weight
        data.to_csv(path_to_csv, index=False, header=True)
    else:
        new_weight.to_csv(path_to_csv, mode='a', index=False, header=False)


def plot_history(period, user_id):
    if period == '1 месяц':
        days = 30
    elif period == '3 месяца':
        days = 90
    else:
        days = 100000
    data = pd.read_csv('data/data.csv', parse_dates=['create_dt'],
                       date_parser=lambda x: pd.to_datetime(x, format='%d.%m.%Y'))
    relevant_data = data[(data.user_id == user_id) & (data.create_dt >= datetime.now() - timedelta(days=days))]
    x = relevant_data.create_dt.values
    y = relevant_data.weight.values
    plt.figure(figsize=(10, 6))
    if len(y) == 0:
        text = "Пока нет истории"
        plt.text(0.5, 0.5, text, ha='center', va='center', fontsize=20)
        plt.axis('off')
    else:
        y_min, y_max, y_center = y.min(), y.max(), (y.min() + y.max()) / 2
        plt.plot(x, y, marker='o', linestyle='-')
        plt.ylabel('Вес')
        plt.title('История одного жиробаса')
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d.%m'))
        plt.ylim(y_center - 2.5 * (y_center - y_min) - 0.1, y_center + 2.5 * (y_max - y_center) + 0.1)
        plt.xlim(x.min() - pd.Timedelta(days=2), x.max() + pd.Timedelta(days=2))
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_object = Image.open(buffer)
    return image_object


if __name__ == '__main__':
    bot.infinity_polling()
