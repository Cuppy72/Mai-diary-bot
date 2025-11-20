import json

import re

import telebot
from telebot import types

from datetime import *

import sys
import subprocess

from telebot.types import InlineKeyboardMarkup
from telebot.types import BotCommand

from parsing_script import falling_process

token = 'Токен телеграм бота'
bot = telebot.TeleBot(token)

commands = [BotCommand("/start", "Начать"),
            BotCommand("/add_homework", "( Доступно только старосте )"),
            BotCommand("/cancel", "( Доступно только старосте )"),
            BotCommand("/del_prev_homework", "( Доступно только старосте )")]
bot.set_my_commands(commands)

hello_message = "Вас приветствует электронный дневник"
name_of_diary_message = "студента МАИ!"
chose_week_message = "<b>Выберите учебный день</b>"

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

admin_list = {"Begemot_anatoliy", "Tketg"}

short_name_of_lessons = {"Программирование на языке Python": "Python", "Физическая культура": "Физра",
                         "Дискретная математика": "Дискретка", "Математический анализ": "Матан",
                         "Основы российской государственности": "ОРГ",
                         "Линейная алгебра и аналитическая геометрия": "Линал ангем", "История России": "История",
                         "Иностранный язык": "Английский", "Общественный проект \"Обучение служением\"": "Обучение",
                         "Фундаментальная информатика": "Фунда",
                         "Введение в авиационную и ракетно-космическую технику": "ВАРКТ"}

bot_global_message_id = None

button_for_left_week = types.InlineKeyboardButton(text="⬅️", callback_data="prev_week")
button_for_right_week = types.InlineKeyboardButton(text="➡️", callback_data="next_week")
button_for_current_week = types.InlineKeyboardButton(text="🏠", callback_data="current_week")
button_back = types.InlineKeyboardButton(text='Вернуться назад', callback_data='back')

homework_to_date = None
homework_to_lesson_name = None
homework_to_lesson_type = None

homework_state = False
delete_or_add_state = False


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
        create_file = open("user_data.json", "w", encoding="utf-8")
        create_file.close()
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
    return


def create_lesson_button(name_lesson, type_lesson):
    button = types.InlineKeyboardButton(text=f"{name_lesson} - {type_lesson}",
                                        callback_data=f"{name_lesson}-{type_lesson}")
    return button


@bot.message_handler(commands=["del_homework"])
def delete_choise_homework(message):
    global delete_or_add_state
    delete_or_add_state = True
    admin_panel(message)
    return


@bot.message_handler(commands=["del_prev_homework"])
def delete_prev_homework(message):
    global homework_to_date, homework_to_lesson_name, homework_to_lesson_type

    if message.from_user.username in admin_list:
        if homework_to_lesson_name is None and homework_to_date is None:
            bot.send_message(message.chat.id, "<u><i>В текущей сессии домашнее задание ещё не было добавлено</i></u>",
                             parse_mode="HTML")
        else:
            with open("schedule.json", "r", encoding="utf-8") as homework_file:
                homework_dict = json.load(homework_file)

            for choise_homework in homework_dict[homework_to_date]:
                for name_choise_lesson in choise_homework:
                    if homework_to_lesson_name in name_choise_lesson and homework_to_lesson_type == \
                            choise_homework[name_choise_lesson]["type"]:
                        choise_homework[name_choise_lesson]["homework"] = "Домашнего задания нет"

            homework_to_lesson_name, homework_to_lesson_type, homework_to_date = None, None, None
            with open("schedule.json", "w", encoding="utf-8") as homework_file:
                json.dump(homework_dict, homework_file, ensure_ascii=False, indent=4)
            bot.send_message(message.chat.id, "<i>Домашнее задание успешно удалено</i>", parse_mode="HTML")
    return


@bot.message_handler(commands=["add_homework"])
def admin_panel(message):
    global homework_state
    homework_state = True
    if message.from_user.username in admin_list:
        bot.send_message(message.chat.id, "<i>Введите дату в формате год-месяц-день</i>", parse_mode="HTML")
        bot.register_next_step_handler(message, group_num)
        return


def admin_panel_quit(message):
    global homework_state
    homework_state = False
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.send_message(message.chat.id, "<i>Ввод домашнего задания прерван</i>", parse_mode="HTML")
    return


def check_message(message):
    global homework_state
    homework_state = False
    if check_other_command(message, edit=True):
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.edit_message_text("<i>Ввод домашнего задания прерван</i>", chat_id=message.chat.id,
                              message_id=bot_global_message_id,
                              parse_mode='HTML', reply_markup=None)
        return


def check_other_command(message, edit=False):
    if message.text == "/start" and not edit:
        start_hello_message(message)
        return True
    elif message.text == "/start" and edit:
        start_hello_message(message)
        return True
    elif message.text == "/add_homework" and not edit:
        admin_panel(message)
        return True
    elif message.text == "/add_homework" and edit:
        admin_panel(message)
        return True
    elif message.text == "/cancel" and not edit:
        admin_panel_quit(message)
        return True
    elif message.text == "/cancel" and edit:
        return True
    return None


def group_num(message):
    global homework_to_date

    if check_other_command(message):
        return

    input_date = message.text

    try:
        year, month, day = [int(i) for i in input_date.split("-")]
        if current_date_valid(day, month, year) == False:
            bot.send_message(message.chat.id, "<i><u>Некорректная дата. Попробуйте ещё раз</u></i>", parse_mode="HTML")
            bot.register_next_step_handler(message, group_num)
            return
        else:
            homework_to_date = input_date
            choise_lesson(message)
            return
    except ValueError:
        bot.send_message(message.chat.id, "<i><u>Ввод должен совпадать с форматом даты. Попробуйте ещё раз</u></i>",
                         parse_mode="HTML")
        bot.register_next_step_handler(message, group_num)
        return


def choise_lesson(message):
    global homework_to_lesson_name, bot_global_message_id

    keyboard = types.InlineKeyboardMarkup()
    try:
        with open("schedule.json", "r", encoding="utf-8") as data_file:
            full_name_lessons_on_input_date = json.load(data_file)[homework_to_date]
    except KeyError:
        bot.send_message(message.chat.id, "<i><u>Расписание на выбранную дату отсутствует. Попробуйте ещё раз</u></i>",
                         parse_mode="HTML")
        admin_panel(message)
        return

    lessons_dict = []
    for one_lesson_on_day in full_name_lessons_on_input_date:
        for not_beautiful_name in one_lesson_on_day:
            short_name = short_name_of_lessons[not_beautiful_name[:not_beautiful_name.find("<") - 1]]
            lesson_n_type = {short_name: one_lesson_on_day[not_beautiful_name]["type"]}
            if lesson_n_type not in lessons_dict:
                lessons_dict.append(lesson_n_type)

    for i in lessons_dict:
        for j in i:
            name_lesson = j
            type_lesson = i[j]
            keyboard.add(create_lesson_button(name_lesson, type_lesson))
    if not delete_or_add_state:
        bot_message = bot.send_message(message.chat.id, "Выберете предмет для добавления домашнего задания",
                                       parse_mode='HTML',
                                       reply_markup=keyboard)
    else:
        bot_message = bot.send_message(message.chat.id, "Выберете предмет для удаления домашнего задания",
                                       parse_mode='HTML',
                                       reply_markup=keyboard)
    bot_global_message_id = bot_message.message_id
    bot.register_next_step_handler(bot_message, check_message)


def homework_from_admin(message):
    if check_other_command(message):
        return

    input_homework = message.text

    with open('schedule.json', "r", encoding="utf-8") as add_homework_file:
        current_schedule_and_homework = json.load(add_homework_file)

    for lesson_dict in current_schedule_and_homework[homework_to_date]:
        for name_lesson in lesson_dict:
            if homework_to_lesson_name in name_lesson and lesson_dict[name_lesson][
                "type"] == homework_to_lesson_type:
                lesson_dict[name_lesson]["homework"] = input_homework

    with open("schedule.json", "w", encoding="utf-8") as add_homework_file:
        json.dump(current_schedule_and_homework, add_homework_file, ensure_ascii=False, indent=4)

    bot.send_message(message.chat.id, "<i>Домашнее задание успешно добавлено</i>", parse_mode="HTML")
    return


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
    return


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
    return


@bot.callback_query_handler(func=lambda call: True)
def week_buttons(call):
    global current_day, current_month, current_year, homework_to_lesson_name, homework_to_lesson_type, homework_to_date
    global delete_or_add_state
    bot.answer_callback_query(call.id)
    current_day, current_month, current_year = data_load(call.from_user.username).values()

    if call.data == 'prev_week':

        current_day, current_month = start_of_the_week(current_day, current_month)
        current_day, current_month = date_decrease(current_day, current_month)

        current_day, current_month = start_of_the_week(current_day, current_month)

        update_values(call.from_user.username)
        repeat_hello_message(call)
        return

    elif call.data == 'next_week':
        current_day, current_month = start_of_the_week(current_day, current_month)
        for _ in range(7):
            current_day, current_month = date_increase(current_day, current_month)

        update_values(call.from_user.username)
        repeat_hello_message(call)
        return

    elif call.data == 'current_week':
        if start_of_the_week(now_day, now_month) == start_of_the_week(current_day, current_month):
            return
        else:
            current_year = now_year
            current_month = now_month
            current_day = now_day

            update_values(call.from_user.username)
            repeat_hello_message(call)
        return

    elif re.fullmatch("\d{4}-\d{2}-\d{2}", call.data):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button_back)
        with open("schedule.json", "r", encoding='utf-8') as schedule_file:
            schedule_date = json.load(schedule_file)

        if falling_process:
            all_text = '<i>Сервис временно недоступен(</i>'
        else:
            formating = "%Y-%m-%d"
            name_of_chose_day = name_of_day_accusative_case[datetime.strptime(call.data, formating).weekday()]

            if schedule_date.get(call.data) is None:
                all_text = f"<b><i>Расписание на {name_of_chose_day} отсутствует</i></b>"
            else:
                lessons_list = schedule_date[call.data]
                all_text = f"<b>Расписание на {name_of_chose_day}</b>\n\n"

                for current_lesson in lessons_list:
                    for name_of_current_lesson in current_lesson:
                        homework = current_lesson[name_of_current_lesson]["homework"]
                        all_text += name_of_current_lesson + '\n' + f'<blockquote>{homework}</blockquote>' + '\n\n\n'

        bot.edit_message_text(all_text, chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=keyboard, parse_mode='HTML')
        return

    elif call.data == "back":
        update_values(call.from_user.username)
        repeat_hello_message(call)
        return

    else:
        if homework_state:
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            short_name_call_data, homework_to_lesson_type = call.data.split("-")

            for full_name in short_name_of_lessons:
                if short_name_of_lessons[full_name] == short_name_call_data:
                    homework_to_lesson_name = full_name

            if not delete_or_add_state:
                bot.send_message(call.message.chat.id, "<i>Введите домашнее задание</i>", parse_mode="HTML")
                bot.register_next_step_handler(call.message, homework_from_admin)
                return
            else:
                with open('schedule.json', "r", encoding="utf-8") as add_homework_file:
                    current_schedule_and_homework = json.load(add_homework_file)

                for lesson_dict in current_schedule_and_homework[homework_to_date]:
                    for name_lesson in lesson_dict:
                        if homework_to_lesson_name in name_lesson and lesson_dict[name_lesson][
                            "type"] == homework_to_lesson_type:
                            lesson_dict[name_lesson]["homework"] = "Домашнего задания нет"

                with open("schedule.json", "w", encoding="utf-8") as add_homework_file:
                    json.dump(current_schedule_and_homework, add_homework_file, ensure_ascii=False, indent=4)

                homework_to_date, homework_to_lesson_name, homework_to_lesson_type = None, None, None
                delete_or_add_state = False

                bot.send_message(call.message.chat.id, "<i>Домашнее задание успешно удалено</i>", parse_mode="HTML")
                return


bot.infinity_polling()
