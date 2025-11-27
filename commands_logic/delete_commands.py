import json
import commands_logic.add_command as ac

def delete_prev():
    with open("databases/schedule.json", "r", encoding="utf-8") as homework_file:
        homework_dict = json.load(homework_file)

    for choise_homework in homework_dict[ac.homework_to_date]:
        for name_choise_lesson in choise_homework:
            if ac.homework_to_lesson_name in name_choise_lesson and ac.homework_to_lesson_type == \
                    choise_homework[name_choise_lesson]["type"]:
                choise_homework[name_choise_lesson]["homework"] = "Домашнего задания нет"

    ac.homework_to_lesson_name, ac.homework_to_lesson_type, ac.homework_to_date = None, None, None
    with open("databases/schedule.json", "w", encoding="utf-8") as homework_file:
        json.dump(homework_dict, homework_file, ensure_ascii=False, indent=4)

def delete_input():
    with open('databases/schedule.json', "r", encoding="utf-8") as add_homework_file:
        current_schedule_and_homework = json.load(add_homework_file)

    for lesson_dict in current_schedule_and_homework[ac.homework_to_date]:
        for name_lesson in lesson_dict:
            if ac.homework_to_lesson_name in name_lesson and lesson_dict[name_lesson][
                "type"] == ac.homework_to_lesson_type:
                if lesson_dict[name_lesson]["homework"] == "Домашнего задания нет":
                    return False
                lesson_dict[name_lesson]["homework"] = "Домашнего задания нет"

    with open("databases/schedule.json", "w", encoding="utf-8") as add_homework_file:
        json.dump(current_schedule_and_homework, add_homework_file, ensure_ascii=False, indent=4)

    ac.homework_to_date, ac.homework_to_lesson_name, ac.homework_to_lesson_type = None, None, None
    return True