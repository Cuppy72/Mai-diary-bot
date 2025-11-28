import json

import re
import textwrap as tw

from datetime import *

import sys
import subprocess

import telebot

from telebot import types

from telebot.types import InlineKeyboardMarkup
from telebot.types import BotCommand

import helpers_libs.weeks_operations as wk
import commands_logic.global_command as gc
import commands_logic.add_command as ac

from helpers_libs.parsing_script import falling_process
from helpers_libs.user_date_operations import data_load, data_update, update_values
from helpers_libs.weeks_operations import current_date_valid, date_decrease, date_increase, start_of_the_week, \
    create_week_list
from commands_logic.global_command import next_panel, prev_panel, global_homework_for_user
from commands_logic.add_command import add_lessons_keyboard, add_homework
from commands_logic.delete_commands import delete_prev, delete_input

token = '8242607343:AAFw_2O5UfJBxBnZe5YquaZ38_rY_4Uhah0'
bot = telebot.TeleBot(token)

commands = [BotCommand("/start", "Начать"),
            BotCommand("/help", "Краткое описание доступных команд"),
            BotCommand("/global", "Просмотр глобального ДЗ"),
            BotCommand("/add_global", "( Доступно только старосте )"),
            BotCommand("/add", "( Доступно только старосте )"),
            BotCommand("/del_prev", "( Доступно только старосте )"),
            BotCommand("/del", "( Доступно только старосте )"),
            BotCommand("/cancel", "( Доступно только старосте )")]
bot.set_my_commands(commands)

hello_text = tw.fill(tw.dedent("Вас приветствует электронный дневник студента МАИ!").strip(), width=28,
                     initial_indent='',
                     subsequent_indent='⠀' * 2 + "  ")
choise_text = "⠀" * 2 + " " + "<b>Выберите учебный день</b>"

Title_message = hello_text + "\n\n" + choise_text

homework_name = "Домашнее задание на "

now_day = date.today().day
now_month = date.today().month
now_year = date.today().year

name_of_day_accusative_case = {0: "понедельник", 1: "вторник", 2: "среду", 3: "четверг", 4: "пятницу", 5: "субботу",
                               6: "воскресенье"}

subprocess.run([sys.executable, 'helpers_libs/parsing_script.py'])

admin_list = {"Begemot_anatoliy", "Tketg"}

bot_global_message_id = None

button_for_left_week = types.InlineKeyboardButton(text="⬅️", callback_data="prev_week")
button_for_right_week = types.InlineKeyboardButton(text="➡️", callback_data="next_week")
button_for_current_week = types.InlineKeyboardButton(text="🏠", callback_data="current_week")
button_back = types.InlineKeyboardButton(text='Вернуться назад', callback_data='back')

global_homework_state = False

homework_state = False
delete_or_add_state = False


@bot.message_handler(commands=["help"])
def help_command(message):
    if message.from_user.username in admin_list:
        bot.send_message(message.chat.id,
                         "<b><i>Список команд и их функционал</i></b>:\n\n"
                         "<i>/start - Вывод расписания вместе с домашним заданием на конкретную неделю\n\n"
                         "/global - Вывод глобального домашнего задания с указанием дедлайнов\n\n"
                         "/add_global - Добавление глобального домашнего задания\n\n"
                         "/add - Добавление домашнего задания к выбранному дню\n\n"
                         "/cancel - Отмена ввода домашнего задания\n\n"
                         "/del - Удаление домашнего задания на выбранный день\n\n"
                         "/del_prev - Удаление недавно добавленного домашнего задания</i>",
                         parse_mode="HTML")
    else:
        bot.send_message(message.chat.id,
                         "<b><i>Список команд и их функционал</i></b>:\n\n"
                         "<i>/start - Вывод расписания вместе с прикрепленным домашним заданием на конкретную неделю\n\n"
                         "/global - Вывод глобальных задания с указанием дедлайнов</i>",
                         parse_mode="HTML")
    return


@bot.message_handler(commands=["add_global"])
def create_start_panel_date(message):
    global global_homework_state
    global_homework_state = True

    bot.send_message(message.chat.id, "<i>Введите дату дедлайна в формате год-месяц-день</i>", parse_mode="HTML")
    bot.register_next_step_handler(message, group_num, another_check=True)


def create_start_panel_lessons(message):
    global bot_global_message_id
    keyboard = gc.create_start_panel()
    bot_message = bot.send_message(message.chat.id,
                                   "<i>Выберите предмет для указания глобального домашнего задания</i>",
                                   parse_mode="HTML", reply_markup=keyboard)
    bot_global_message_id = bot_message.message_id
    bot.register_next_step_handler(message, check_message)


@bot.message_handler(commands=["del"])
def delete_choise_homework(message):
    global delete_or_add_state
    delete_or_add_state = True
    admin_panel(message)
    return


@bot.message_handler(commands=["global"])
def show_globals(message):
    text = global_homework_for_user()
    bot.send_message(message.chat.id, text, parse_mode="HTML")


@bot.message_handler(commands=["del_prev"])
def delete_prev_homework(message):
    if message.from_user.username in admin_list:
        if ac.homework_to_lesson_name is None or ac.homework_to_date is None or ac.homework_to_lesson_type is None:
            bot.send_message(message.chat.id, "<u><i>В текущей сессии домашнее задание ещё не было добавлено</i></u>",
                             parse_mode="HTML")
        else:
            delete_prev()
            bot.send_message(message.chat.id, "<i>Домашнее задание успешно удалено</i>", parse_mode="HTML")
    return


@bot.message_handler(commands=["add"])
def admin_panel(message):
    global delete_or_add_state
    if not delete_or_add_state:
        global homework_state
        homework_state = True

    if message.from_user.username in admin_list:
        bot.send_message(message.chat.id, "<i>Введите дату в формате год-месяц-день</i>", parse_mode="HTML")
        bot.register_next_step_handler(message, group_num)
        return


def admin_panel_quit(message):
    bot.send_message(message.chat.id, "<i>Ввод прерван</i>", parse_mode="HTML")
    return


def check_message(message):
    if check_other_command(message, edit=True):
        bot.edit_message_text("<i>Ввод прерван</i>", chat_id=message.chat.id,
                              message_id=bot_global_message_id,
                              parse_mode='HTML', reply_markup=None)
    else:
        bot.register_next_step_handler(message, check_message)
    return


def check_other_command(message, edit=False):
    global homework_state, global_homework_state, delete_or_add_state
    message_from_user = message.text
    if message_from_user.startswith("/"):
        homework_state = False
        global_homework_state = False
        delete_or_add_state = False
        bot.clear_step_handler_by_chat_id(message.chat.id)
        ac.homework_to_date, ac.homework_to_lesson_name, ac.homework_to_lesson_type = None, None, None

        if message_from_user == "/start" and edit:
            start_hello_message(message)
            return True

        elif message_from_user == "/start":
            admin_panel_quit(message)
            start_hello_message(message)
            return True

        elif message_from_user == "/add" and edit:
            admin_panel(message)
            return True

        elif message_from_user == "/add":
            admin_panel_quit(message)
            admin_panel(message)
            return True

        elif message_from_user == "/cancel" and edit:
            return True

        elif message_from_user == "/cancel":
            admin_panel_quit(message)
            return True

        elif message_from_user == "/del" and edit:
            delete_choise_homework(message)
            return True

        elif message_from_user == "/del":
            admin_panel_quit(message)
            delete_choise_homework(message)
            return True

        elif message_from_user == "/del_prev" and edit:
            delete_prev_homework(message)
            return True

        elif message_from_user == "/del_prev":
            admin_panel_quit(message)
            delete_prev_homework(message)
            return True

        elif message_from_user == '/global' and edit:
            show_globals(message)
            return True

        elif message_from_user == '/global':
            admin_panel_quit(message)
            show_globals(message)
            return True

        elif message_from_user == '/add_global' and edit:
            create_start_panel_date(message)
            return True

        elif message_from_user == '/add_global':
            admin_panel_quit(message)
            create_start_panel_date(message)
            return True

        elif message_from_user == '/help' and edit:
            help_command(message)
            return True

        elif message_from_user == '/help':
            admin_panel_quit(message)
            help_command(message)
            return True

    return False


def group_num(message, another_check=False):
    if check_other_command(message):
        return

    input_date = message.text

    if re.fullmatch("\d{4}-\d{1,2}-\d{1,2}", input_date):
        year, month, day = [int(i) for i in input_date.split("-")]
        if not current_date_valid(day, month, year):
            bot.send_message(message.chat.id, "<i><u>Некорректная дата. Попробуйте ещё раз</u></i>", parse_mode="HTML")
            bot.register_next_step_handler(message, group_num, another_check=another_check)
            return
        else:
            correct_write_date = f"{year}-{str(month).rjust(2, '0')}-{str(day).rjust(2, '0')}"

            if another_check:
                if datetime(year, month, day) < datetime.now():
                    bot.send_message(message.chat.id,
                                     "<i><u>Дата дедлайна глобального ДЗ не может быть раньше сегодняшней. Попробуйте ещё раз</u></i>",
                                     parse_mode="HTML")
                    bot.register_next_step_handler(message, group_num, another_check=another_check)
                    return
                else:
                    gc.global_dedline = correct_write_date
                    create_start_panel_lessons(message)
                    return

            with open("databases/schedule.json", "r", encoding="utf-8") as schedule_file:
                valid = True if correct_write_date in json.load(schedule_file) else False
            if valid:
                ac.homework_to_date = correct_write_date
                choise_lesson(message)
                return
            else:
                bot.send_message(message.chat.id,
                                 "<i><u>Расписание на выбранную дату отсутствует. Попробуйте ещё раз</u></i>",
                                 parse_mode="HTML")
                bot.register_next_step_handler(message, group_num, another_check=another_check)
                return
    else:
        bot.send_message(message.chat.id, "<i><u>Ввод должен совпадать с форматом даты. Попробуйте ещё раз</u></i>",
                         parse_mode="HTML")
        bot.register_next_step_handler(message, group_num, another_check=another_check)
        return


def choise_lesson(message):
    global bot_global_message_id, delete_or_add_state
    keyboard = add_lessons_keyboard()

    if not delete_or_add_state:
        bot_message = bot.send_message(message.chat.id, "Выберите предмет для добавления домашнего задания",
                                       parse_mode='HTML',
                                       reply_markup=keyboard)
    else:
        bot_message = bot.send_message(message.chat.id, "Выберите предмет для удаления домашнего задания",
                                       parse_mode='HTML',
                                       reply_markup=keyboard)
    bot_global_message_id = bot_message.message_id
    bot.register_next_step_handler(message, check_message)


def homework_from_admin(message, global_homework=False):
    global global_homework_state, homework_state
    if check_other_command(message):
        return

    add_homework(message.text, global_homework=global_homework)
    global_homework_state = False
    homework_state = False
    if not global_homework:
        bot.send_message(message.chat.id, "<i>Домашнее задание успешно добавлено</i>", parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "<i>Глобальное домашнее задание успешно добавлено</i>", parse_mode="HTML")
    return


@bot.message_handler(commands=['start'])
def start_hello_message(message):
    keyboard = types.InlineKeyboardMarkup()

    wk.current_day, wk.current_month, wk.current_year = data_load(message.from_user.username).values()
    wk.current_day, wk.current_month, wk.current_year = data_update(message.from_user.username,
                                                                    current_day=now_day,
                                                                    current_month=now_month,
                                                                    current_year=now_year).values()

    start_day, start_month = start_of_the_week(wk.current_day, wk.current_month)
    week_list = create_week_list(start_day, start_month)

    update_values(message.from_user.username)

    for i in week_list:
        keyboard.add(i)
    keyboard.add(button_for_left_week, button_for_current_week, button_for_right_week)

    bot.send_message(message.chat.id, Title_message, parse_mode='HTML',
                     reply_markup=keyboard)
    return


def repeat_hello_message(call):
    keyboard = types.InlineKeyboardMarkup()
    wk.current_day, wk.current_month, wk.current_year = data_load(call.from_user.username).values()

    start_day, start_month = start_of_the_week(wk.current_day, wk.current_month)
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
    global delete_or_add_state, homework_state
    bot.answer_callback_query(call.id)
    wk.current_day, wk.current_month, wk.current_year = data_load(call.from_user.username).values()

    if call.data == 'prev_week':

        wk.current_day, wk.current_month = start_of_the_week(wk.current_day, wk.current_month)
        wk.current_day, wk.current_month = date_decrease(wk.current_day, wk.current_month)

        wk.current_day, wk.current_month = start_of_the_week(wk.current_day, wk.current_month)

        update_values(call.from_user.username)
        repeat_hello_message(call)
        return

    elif call.data == 'next_week':
        wk.current_day, wk.current_month = start_of_the_week(wk.current_day, wk.current_month)
        for _ in range(7):
            wk.current_day, wk.current_month = date_increase(wk.current_day, wk.current_month)

        update_values(call.from_user.username)
        repeat_hello_message(call)
        return

    elif call.data == 'current_week':
        if start_of_the_week(now_day, now_month) == start_of_the_week(wk.current_day, wk.current_month):
            return
        else:
            wk.current_year = now_year
            wk.current_month = now_month
            wk.current_day = now_day

            update_values(call.from_user.username)
            repeat_hello_message(call)
        return

    elif re.fullmatch("\d{4}-\d{1,2}-\d{1,2}", call.data):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button_back)
        with open("databases/schedule.json", "r", encoding='utf-8') as schedule_file:
            schedule_date = json.load(schedule_file)

        if falling_process:
            all_text = '<i>Сервис временно недоступен(</i>'
        else:
            name_of_chose_day = name_of_day_accusative_case[datetime.strptime(call.data, gc.formating).weekday()]

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

    elif global_homework_state and call.data == "left":
        keyboard = prev_panel()
        bot.edit_message_text("<i>Выберите предмет для указания глобального домашнего задания</i>",
                              chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=keyboard, parse_mode='HTML')

    elif global_homework_state and call.data == "right":
        keyboard = next_panel()
        bot.edit_message_text("<i>Выберите предмет для указания глобального домашнего задания</i>",
                              chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=keyboard, parse_mode='HTML')
    elif "global" in call.data and global_homework_state:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        name_call_data = call.data
        short_name_call_data = name_call_data[:name_call_data.find("global") - 1]

        for full_name in gc.short_name_of_lessons:
            if gc.short_name_of_lessons[full_name] == short_name_call_data:
                ac.homework_to_lesson_name = full_name
                break

        bot.send_message(call.message.chat.id, "<i>Введите глобальное домашнее задание</i>", parse_mode="HTML")
        bot.register_next_step_handler(call.message, homework_from_admin, global_homework=True)
        return

    else:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        short_name_call_data, ac.homework_to_lesson_type = call.data.split("-")

        for full_name in gc.short_name_of_lessons:
            if gc.short_name_of_lessons[full_name] == short_name_call_data:
                ac.homework_to_lesson_name = full_name
                break

        if homework_state:
            bot.send_message(call.message.chat.id, "<i>Введите домашнее задание</i>", parse_mode="HTML")
            bot.register_next_step_handler(call.message, homework_from_admin, global_homework=False)
            return

        elif delete_or_add_state:

            flag = delete_input()
            if not flag:
                bot.send_message(call.message.chat.id,
                                 "<i><u>Домашнее задание на выбранное занятие ещё не добавлено</u></i>",
                                 parse_mode="HTML")
                return

            ac.homework_to_date, ac.homework_to_lesson_name, ac.homework_to_lesson_type = None, None, None
            delete_or_add_state = False

            bot.send_message(call.message.chat.id, "<i>Домашнее задание успешно удалено</i>", parse_mode="HTML")
            return



bot.infinity_polling()
