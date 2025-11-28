import json
from importlib.resources import read_text

import commands_logic.add_command as ac

from datetime import *
from telebot import types
from helpers_libs.weeks_operations import name_of_day

formating = "%Y-%m-%d"
many_all_lessons = set()

global_dedline = None

first_inisialisation = True

month_date_dict = {12: "декабря", 1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
                   7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября"}

short_name_of_lessons = {"Программирование на языке Python": "Python", "Физическая культура": "Физра",
                         "Дискретная математика": "Дискретка", "Математический анализ": "Матан",
                         "Основы российской государственности": "ОРГ",
                         "Линейная алгебра и аналитическая геометрия": "Линал ангем", "История России": "История",
                         "Иностранный язык": "Английский", "Общественный проект \"Обучение служением\"": "Обучение",
                         "Фундаментальная информатика": "Фунда",
                         "Введение в авиационную и ракетно-космическую технику": "ВАРКТ"}

button_left_action = types.InlineKeyboardButton(text="⬅️", callback_data="left")
button_right_action = types.InlineKeyboardButton(text="➡️", callback_data="right")

false_generator_index = 0


def next_value(name_lessons_in_dict):
    global false_generator_index
    false_generator_index += 1
    false_generator_index = false_generator_index % len(name_lessons_in_dict)

    return name_lessons_in_dict[false_generator_index % len(name_lessons_in_dict)]


def create_button_for_global(text, callback):
    button = types.InlineKeyboardButton(text=text, callback_data=callback)
    return button


def create_many_all_lessons():
    many = set()
    count_add_days = 0

    flag_start_week = False

    with open("databases/schedule.json", "r", encoding="utf-8") as all_lessons_file:
        all_lessons = json.load(all_lessons_file)

    for current_date in all_lessons:
        if datetime.strptime(current_date, formating).weekday() == 0:
            flag_start_week = True

        if flag_start_week:
            for current_lesson in all_lessons[current_date]:
                for name_lesson in current_lesson:
                    many.add(
                        f"{short_name_of_lessons[name_lesson[:name_lesson.find('<') - 1]]}")
            count_add_days += 1
            if count_add_days == 6:
                break

    return sorted(many)


def create_start_panel():
    global false_generator_index, many_all_lessons, first_inisialisation

    if first_inisialisation:
        many_all_lessons = create_many_all_lessons()
        first_inisialisation = False

    false_generator_index = 0

    keyboard = types.InlineKeyboardMarkup()

    for i in range(4):
        short_name = next_value(many_all_lessons)
        callback_full_name = short_name + " global"

        button = create_button_for_global(short_name, callback_full_name)
        keyboard.add(button)
    keyboard.add(button_left_action, button_right_action)

    return keyboard


def next_panel():
    keyboard = types.InlineKeyboardMarkup()

    for i in range(4):
        short_name = next_value(list(many_all_lessons))
        callback_full_name = short_name + " global"

        button = create_button_for_global(short_name, callback_full_name)
        keyboard.add(button)
    keyboard.add(button_left_action, button_right_action)
    return keyboard


def prev_panel():
    global false_generator_index
    keyboard = types.InlineKeyboardMarkup()

    false_generator_index -= 8
    for i in range(4):
        short_name = next_value(list(many_all_lessons))
        callback_full_name = short_name + " global"

        button = create_button_for_global(short_name, callback_full_name)
        keyboard.add(button)
    keyboard.add(button_left_action, button_right_action)
    return keyboard


def add_func_for_global_homework(text):
    try:
        with open('databases/global_homework.json', "r", encoding="utf-8") as add_global_homework_file:
            global_homework_dict = json.load(add_global_homework_file)
    except FileNotFoundError:
        global_homework_dict = {ac.homework_to_lesson_name: [{"homework": text, "deadline": global_dedline}]}

        with open("databases/global_homework.json", "w", encoding="utf-8") as add_global_homework_file:
            json.dump(global_homework_dict, add_global_homework_file, ensure_ascii=False, indent=4)
        return

    if ac.homework_to_lesson_name in global_homework_dict:
        global_homework_dict[ac.homework_to_lesson_name].append({"homework": text, "deadline": global_dedline})
    else:
        global_homework_dict[ac.homework_to_lesson_name] = [{"homework": text, "deadline": global_dedline}]

    with open("databases/global_homework.json", "w", encoding="utf-8") as add_global_homework_file:
        json.dump(global_homework_dict, add_global_homework_file, ensure_ascii=False, indent=4)
    return


def del_func_for_global_homework():
    pass


def auto_global_del(name, homework):
    with open("databases/global_homework.json", "r", encoding="utf-8") as global_homework_file:
        global_homework_dict = json.load(global_homework_file)

    for name_lesson in global_homework_dict:
        if name_lesson == name:
            if len(global_homework_dict[name_lesson]) == 1:
                del global_homework_dict[name_lesson]

                with open("databases/global_homework.json", "w", encoding="utf-8") as global_homework_file:
                    json.dump(global_homework_dict, global_homework_file, ensure_ascii=False, indent=4)

                return
            else:
                for homeworks in global_homework_dict[name_lesson]:
                    if homework in homeworks.values():
                        global_homework_dict[name_lesson].remove(homeworks)

                        with open("databases/global_homework.json", "w", encoding="utf-8") as global_homework_file:
                            json.dump(global_homework_dict, global_homework_file, ensure_ascii=False, indent=4)

                        return


def deadline_name(date_input):
    deadline_date_object = datetime.strptime(date_input, formating)
    name_dedline_day = name_of_day[deadline_date_object.weekday()]

    days_left = (deadline_date_object - datetime.now()).days + 1

    flag_full_name = False

    full_name_deadline = case = None

    if days_left < 0:
        return False
    elif days_left == 0:
        full_name_deadline = "<u><i>СЕГОДНЯ!!!</i></u>"
        flag_full_name = True
    elif days_left == 1:
        case = "день"
    elif days_left < 5:
        case = "дня"
    else:
        case = "дней"

    if not flag_full_name:
        _, month, day = date_input.split("-")
        full_name_deadline = f"{name_dedline_day} {int(day)} {month_date_dict[int(month)]}\n( Через {days_left} {case} )"

    return full_name_deadline


def global_homework_for_user():
    all_text = ''
    text_names = ''
    text_homework = ''
    try:
        with open("databases/global_homework.json", "r", encoding="utf-8") as show_global_homework_file:
            all_global_homework = json.load(show_global_homework_file)

        for name_lesson in all_global_homework:
            text_names += f"<u>{name_lesson}:</u>\n"
            for homework_n_deadlines in all_global_homework[name_lesson]:
                text_homework += f'<blockquote><b><i>Задание</i></b>:\n{homework_n_deadlines["homework"]}\n\n'

                deadline_date = homework_n_deadlines["deadline"]
                full_name_deadline = deadline_name(deadline_date)

                if not full_name_deadline:
                    text_homework = ""
                    auto_global_del(name_lesson, homework_n_deadlines["homework"])
                    continue
                else:
                    text_homework += f'<b><i>Дедлайн</i></b>:\n{full_name_deadline}</blockquote>\n'

            if text_homework != '':
                all_text += text_names
                all_text += text_homework
                text_names = text_homework = ''
                all_text += '\n'
            else:
                text_names = ''

        if all_text != '':
            return all_text
        else:
            text = "<i><u>Глобальное домашнее задание ещё не было добавлено(</u></i>"
            return text

    except FileNotFoundError:
        text = "<i><u>Глобальное домашнее задание ещё не было добавлено(</u></i>"
        return text
