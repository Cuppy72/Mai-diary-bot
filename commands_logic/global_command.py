import json

from datetime import *
from telebot import types

formating = "%Y-%m-%d"
many_all_lessons = set()

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


def create_start_panel():
    global false_generator_index, many_all_lessons
    many_all_lessons = set()
    flag_start_week = False
    count_add_days = 0

    with open("databases/schedule.json", "r", encoding="utf-8") as all_lessons_file:
        all_lessons = json.load(all_lessons_file)

    for current_date in all_lessons:
        if datetime.strptime(current_date, formating).weekday() == 0:
            flag_start_week = True

        if flag_start_week:
            for current_lesson in all_lessons[current_date]:
                for name_lesson in current_lesson:
                    many_all_lessons.add(
                        f"{short_name_of_lessons[name_lesson[:name_lesson.find('<') - 1]]} {current_lesson[name_lesson]['type']}")
            count_add_days += 1
            if count_add_days == 24:
                break

    many_all_lessons = sorted(many_all_lessons)

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
