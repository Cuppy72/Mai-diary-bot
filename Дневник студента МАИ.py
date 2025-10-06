import telebot
from telebot import types
from datetime import *

token = 'Токен телеграмм бота'
bot = telebot.TeleBot(token)

hello_message = "Вас приветствует электронный дневник"
name_of_diary_message = "студента МАИ!"
chose_week_message = "*Выберете учебный день*"

now_day = date.today().day
now_month = date.today().month
now_year = date.today().year

current_day = now_day
current_month = now_month
current_year = now_year

name_of_day = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"}
weeks_dict = {}

button_for_left_week = types.InlineKeyboardButton(text="⬅️", callback_data="prev_week")
button_for_right_week = types.InlineKeyboardButton(text="➡️", callback_data="next_week")
button_for_current_week = types.InlineKeyboardButton(text="🏠", callback_data="current_week")


def create_button(current_date):
    if weeks_dict.get(str(current_date)) is None:
        button = types.InlineKeyboardButton(text=f"{name_of_day[current_date.weekday()]} - "
                                                 f"{str(current_date.day).rjust(2, '0')}."
                                                 f"{str(current_date.month).rjust(2, '0')}",

                                            callback_data=str(current_date))
        weeks_dict.update({str(current_date): button})

        return button
    else:
        return weeks_dict[str(current_date)]


def current_date_valid(day, month, year):
    try:
        current_date = date(year, month, day)
        return current_date

    except ValueError:
        return False


def date_decrease(day, month):
    global current_year
    day -= 1
    if day < 1:
        day = 31
        month -= 1
        if month < 1:
            month = 12
            current_year -= 1

        while current_date_valid(day, month, current_year) == False:
            day -= 1

    return day, month


def date_increase(day, month):
    global current_year
    day += 1
    if current_date_valid(day, month, current_year) != False:

        return day, month
    else:
        day = 1
        month += 1
        if month > 12:
            month = 1
            current_year += 1

        return day, month


def start_of_the_week(day, month):
    while date(current_year, month, day).weekday() != 0:
        day, month = date_decrease(day, month)

    return day, month


def create_week_list(day, month):
    global current_month, current_day
    week = []
    while len(week) < 7:
        if current_date_valid(day, month, current_year) == False:
            day, month = date_increase(day, month)
        current_date = date(current_year, month, day)
        current_month, current_day = month, day
        button = create_button(current_date)
        week.append(button)
        day += 1

    return week


@bot.message_handler(commands=['start'])
def start_hello_message(message):
    keyboard = types.InlineKeyboardMarkup()

    start_day, start_month = start_of_the_week(now_day, now_month)
    week_list = create_week_list(start_day, start_month)

    for i in week_list:
        keyboard.add(i)
    keyboard.add(button_for_left_week, button_for_current_week, button_for_right_week)

    bot.send_message(message.chat.id, hello_message + '\n' + name_of_diary_message.rjust(len(hello_message) + 1) +
                     '\n\n' + chose_week_message.rjust(len(hello_message) + 1), parse_mode='Markdown',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def week_buttons(call):
    global current_day, current_month, current_year
    if call.data == 'prev_week':

        keyboard = types.InlineKeyboardMarkup()

        day, month = start_of_the_week(current_day, current_month)
        day, month = date_decrease(day, month)

        start_day_of_the_week, start_month_of_the_week = start_of_the_week(day, month)

        week_list = create_week_list(start_day_of_the_week, start_month_of_the_week)

        for i in week_list:
            keyboard.add(i)
        keyboard.add(button_for_left_week, button_for_current_week, button_for_right_week)

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboard)

    elif call.data == 'next_week':

        keyboard = types.InlineKeyboardMarkup()

        day, month = start_of_the_week(current_day, current_month)
        for _ in range(7):
            day, month = date_increase(day, month)

        week_list = create_week_list(day, month)

        for i in week_list:
            keyboard.add(i)
        keyboard.add(button_for_left_week, button_for_current_week, button_for_right_week)

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboard)
    elif call.data == 'current_week':
        current_year = now_year

        keyboard = types.InlineKeyboardMarkup()

        day, month = start_of_the_week(now_day, now_month)

        week_list = create_week_list(day, month)

        for i in week_list:
            keyboard.add(i)
        keyboard.add(button_for_left_week, button_for_current_week, button_for_right_week)

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboard)


bot.infinity_polling()
