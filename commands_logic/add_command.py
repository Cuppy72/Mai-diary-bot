import json
import commands_logic.global_command as gc

from telebot import types

homework_to_date = None
homework_to_lesson_name = None
homework_to_lesson_type = None


def create_lesson_button(name_lesson, type_lesson):
    button = types.InlineKeyboardButton(text=f"{name_lesson} - {type_lesson}",
                                        callback_data=f"{name_lesson}-{type_lesson}")
    return button


def add_lessons_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    with open("databases/schedule.json", "r", encoding="utf-8") as data_file:
        full_name_lessons_on_input_date = json.load(data_file)[homework_to_date]

    lessons_dict = []
    for one_lesson_on_day in full_name_lessons_on_input_date:
        for not_beautiful_name in one_lesson_on_day:
            short_name = gc.short_name_of_lessons[not_beautiful_name[:not_beautiful_name.find("<") - 1]]
            lesson_n_type = {short_name: one_lesson_on_day[not_beautiful_name]["type"]}
            if lesson_n_type not in lessons_dict:
                lessons_dict.append(lesson_n_type)

    for i in lessons_dict:
        for j in i:
            name_lesson = j
            type_lesson = i[j]
            keyboard.add(create_lesson_button(name_lesson, type_lesson))
    return keyboard

def add_homework(text, global_homework=False):
    if not global_homework:
        with open('databases/schedule.json', "r", encoding="utf-8") as add_homework_file:
            current_schedule_and_homework = json.load(add_homework_file)

        for lesson_dict in current_schedule_and_homework[homework_to_date]:
            for name_lesson in lesson_dict:
                if homework_to_lesson_name in name_lesson and lesson_dict[name_lesson][
                    "type"] == homework_to_lesson_type:
                    lesson_dict[name_lesson]["homework"] = text

        with open("databases/schedule.json", "w", encoding="utf-8") as add_homework_file:
            json.dump(current_schedule_and_homework, add_homework_file, ensure_ascii=False, indent=4)
    else:
        from commands_logic.global_command import add_func_for_global_homework
        add_func_for_global_homework(text)
        return
