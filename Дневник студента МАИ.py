import json

import telebot
from telebot import types

from datetime import *

import sys
import subprocess

from telebot.types import InlineKeyboardMarkup

from parsing_script import falling_process

token = 'Токен телеграмм бота'
bot = telebot.TeleBot(token)

hello_message = "Вас приветствует электронный дневник"
name_of_diary_message = "студента МАИ!"
chose_week_message = "<b>Выберете учебный день</b>"

Title_message = hello_message + '\n' + name_of_diary_message.rjust(
    len(hello_message) + 1) + '\n\n' + chose_week_message.rjust(len(hello_message) + 6)

homework_name = "Домашнее задание на "

now_day = date.today().day
now_month = date.today().month
now_year = date.today().year

current_day = now_day
current_month = now_month
current_year = now_year

name_of_day = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"}
name_of_day_accusative_case = {0: "понедельник", 1: "вторник", 2: "среду", 3: "четверг", 4: "пятницу", 5: "субботу",
                               6: "воскресенье"}

weeks_dict = {}

subprocess.run([sys.executable, 'parsing_script.py'])

admin_list = {"Begemot_anatoliy"}

with open("schedule.json", "r", encoding='utf-8') as schedule_file:
    schedule_date = json.load(schedule_file)

button_for_left_week = types.InlineKeyboardButton(text="⬅️", callback_data="prev_week")
button_for_right_week = types.InlineKeyboardButton(text="➡️", callback_data="next_week")
button_for_current_week = types.InlineKeyboardButton(text="🏠", callback_data="current_week")
button_back = types.InlineKeyboardButton(text='Вернуться назад', callback_data='back')


def create_button(current_date):
    if str(current_date) not in weeks_dict:
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


def create_new_user_info(username, all_users_date):
    if username not in all_users_date:
        all_users_date[username] = {
            "current_day": now_day,
            "current_month": now_month,
            "current_year": now_year
        }
    return all_users_date


def data_load(username):
    try:
        with open("user_data.json", "r", encoding="utf-8") as data_file:
            all_users_date = json.load(data_file)
        all_users_date = create_new_user_info(username, all_users_date)
    except FileNotFoundError:
        open("user_data.json", "w", encoding="utf-8")
        all_users_date = create_new_user_info(username, {})
    with open("user_data.json", "w", encoding="utf-8") as data_file:
        json.dump(all_users_date, data_file, ensure_ascii=False, indent=4)
    return all_users_date[username]


def data_update(username, **kwargs):
    with open("user_data.json", "r", encoding="utf-8") as data_file:
        all_users_date = json.load(data_file)
    current_user_info = all_users_date[username]
    for old_info in kwargs:
        current_user_info[old_info] = kwargs[old_info]
    all_users_date[username] = current_user_info
    with open("user_data.json", "w", encoding="utf-8") as data_file:
        json.dump(all_users_date, data_file, ensure_ascii=False, indent=4)

    return current_user_info


def update_values(username):
    global current_day, current_month, current_year
    current_day, current_month, current_year = data_update(username,
                                                           current_day=current_day,
                                                           current_month=current_month,
                                                           current_year=current_year).values()


@bot.message_handler(commands=['add_homework'])
def admin_panel(message):
    pass

@bot.message_handler(commands=['start'])
def start_hello_message(message):
    global current_day, current_month, current_year
    keyboard = types.InlineKeyboardMarkup()
    current_day, current_month, current_year = data_load(message.from_user.username).values()
    current_day, current_month, current_year = data_update(message.from_user.username,
                                                           current_day=now_day,
                                                           current_month=now_month,
                                                           current_year=now_year).values()

    start_day, start_month = start_of_the_week(current_day, current_month)
    week_list = create_week_list(start_day, start_month)

    update_values(message.from_user.username)

    for i in week_list:
        keyboard.add(i)
    keyboard.add(button_for_left_week, button_for_current_week, button_for_right_week)

    bot.send_message(message.chat.id, Title_message, parse_mode='HTML',
                     reply_markup=keyboard)


def repeat_hello_message(call):
    global current_day, current_month, current_year
    keyboard = types.InlineKeyboardMarkup()
    current_day, current_month, current_year = data_load(call.from_user.username).values()

    start_day, start_month = start_of_the_week(current_day, current_month)
    week_list = create_week_list(start_day, start_month)

    update_values(call.from_user.username)

    for i in week_list:
        keyboard.add(i)
    keyboard.add(button_for_left_week, button_for_current_week, button_for_right_week)

    bot.edit_message_text(Title_message, chat_id=call.message.chat.id, message_id=call.message.message_id,
                          parse_mode='HTML', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def week_buttons(call):
    global current_day, current_month, current_year
    current_day, current_month, current_year = data_load(call.from_user.username).values()
    if call.data == 'prev_week':

        current_day, current_month = start_of_the_week(current_day, current_month)
        current_day, current_month = date_decrease(current_day, current_month)

        current_day, current_month = start_of_the_week(current_day, current_month)

        update_values(call.from_user.username)
        repeat_hello_message(call)

    elif call.data == 'next_week':

        current_day, current_month = start_of_the_week(current_day, current_month)
        for _ in range(7):
            current_day, current_month = date_increase(current_day, current_month)

        update_values(call.from_user.username)
        repeat_hello_message(call)

    elif call.data == 'current_week':

        if start_of_the_week(now_day, now_month) == start_of_the_week(current_day, current_month):
            bot.answer_callback_query(call.id)
        else:
            current_year = now_year
            current_month = now_month
            current_day = now_day

        update_values(call.from_user.username)
        repeat_hello_message(call)

    elif call.data != 'back':
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button_back)

        if falling_process:
            all_text = '<i>Сервис временно недоступен(</i>'
        else:
            formating = "%Y-%m-%d"
            name_of_chose_day = name_of_day_accusative_case[datetime.strptime(call.data, formating).weekday()]
            if schedule_date.get(call.data) is None:
                all_text = f"<b><i>Расписание на {name_of_chose_day} отсутствует</i></b>"
            else:
                lessons_list = schedule_date[call.data]['lessons_name']
                all_text = f"<b>Расписание на {name_of_chose_day}</b>\n\n"

                for current_lesson in lessons_list:
                    for name_of_current_lesson in current_lesson:
                        homework = current_lesson[name_of_current_lesson]["homework"]
                        all_text += name_of_current_lesson + '\n' + f'<blockquote>{homework}</blockquote>' + '\n\n'

        bot.edit_message_text(all_text, chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=keyboard, parse_mode='HTML')

    else:
        update_values(call.from_user.username)
        repeat_hello_message(call)


bot.infinity_polling()
