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
name_of_day_in_accusative_case = {
    0: "Понедельник", 1: "Вторник", 2: "Среду", 3: "Четверг", 4: "Пятницу", 5: "Субботу", 6: "Воскресенье"
}

weeks_dict = {}

subprocess.run([sys.executable, 'parsing_script.py'])

with open("schedule.json", "r", encoding='utf-8') as schedule_file:
    schedule_date = json.load(schedule_file)

button_for_left_week = types.InlineKeyboardButton(text="⬅️", callback_data="prev_week")
button_for_right_week = types.InlineKeyboardButton(text="➡️", callback_data="next_week")
button_for_current_week = types.InlineKeyboardButton(text="🏠", callback_data="current_week")
button_back = types.InlineKeyboardButton(text='Вернуться назад', callback_data='back')

create_or_edit = False


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
    global create_or_edit
    keyboard = types.InlineKeyboardMarkup()

    start_day, start_month = start_of_the_week(current_day, current_month)
    week_list = create_week_list(start_day, start_month)

    for i in week_list:
        keyboard.add(i)
    keyboard.add(button_for_left_week, button_for_current_week, button_for_right_week)
    if create_or_edit:
        bot.edit_message_text(Title_message, chat_id=message.chat.id, message_id=message.message_id,
                              parse_mode='HTML', reply_markup=keyboard)
        create_or_edit = False
    else:
        bot.send_message(message.chat.id, Title_message, parse_mode='HTML',
                         reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def week_buttons(call):
    global current_day, current_month, current_year, create_or_edit
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

        if start_of_the_week(now_day, now_month) == start_of_the_week(current_day, current_month):
            bot.answer_callback_query(call.id)
        else:
            current_year = now_year
            current_month = now_month
            current_day = now_day

            create_or_edit = True
            start_hello_message(call.message)

    elif call.data != 'back':
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button_back)

        callback_year, callback_month, callback_day = [int(x) for x in call.data.split('-')]
        accusative_case = name_of_day_in_accusative_case[date(callback_year, callback_month, callback_day).weekday()]

        if falling_process:
            all_text = '<i>Сервис временно недоступен(</i>'
        else:
            if schedule_date.get(call.data) is None:
                all_text = f"Расписание на {accusative_case.lower()} отсутствует"
            else:
                all_text = f"<b>{homework_name}{accusative_case.lower()}:</b>\n"
                for lesson_name in schedule_date[call.data]:
                    all_text += '\n' + lesson_name + '\n'
                    all_text += '<blockquote>Дз нет</blockquote>'
                    all_text += '\n'
                all_text = all_text.rstrip()
        bot.edit_message_text(all_text, chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=keyboard, parse_mode='HTML')
    else:
        create_or_edit = True
        start_hello_message(call.message)


bot.infinity_polling()
