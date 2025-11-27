import requests
import hashlib
import json

flag_read = False
falling_process = False

name_group = 'М8О-113БВ-25'

try:
    with open("databases/schedule.json", "r", encoding='utf-8') as file_schedule:
        schedule = json.load(file_schedule)
    flag_read = True

except json.decoder.JSONDecodeError:
    pass

except FileNotFoundError:
    create_file = open("databases/schedule.json", "w", encoding='utf-8')
    create_file.close()

if not flag_read:

    def hash_md5(name):
        md5_hash = hashlib.md5()
        md5_hash.update(name.encode('utf-8'))
        return md5_hash.hexdigest()


    link = f'https://public.mai.ru/schedule/data/{hash_md5(name_group)}.json'

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    req = requests.get(link, headers=headers)

    if req.status_code != 200:
        falling_process = True
    else:
        parse_date = eval(req.text)
        schedule = {}

        for current_date in parse_date:
            if current_date != 'group':
                date = '-'.join(current_date.split('.')[::-1])
                name_day = parse_date[current_date]["day"]

                for time_start in parse_date[current_date]["pairs"]:
                    for lesson_name in parse_date[current_date]["pairs"][time_start]:

                        start_lesson_time = parse_date[current_date]["pairs"][time_start][lesson_name]['time_start'][
                            :-3]
                        end_lesson_time = parse_date[current_date]["pairs"][time_start][lesson_name]['time_end'][:-3]

                        type_lesson = None

                        for current_type in parse_date[current_date]["pairs"][time_start][lesson_name]["type"]:
                            type_lesson = current_type
                        lesson_name = f"{lesson_name} <u><i>{type_lesson}</i></u>\n<i>( {start_lesson_time} - {end_lesson_time} )</i>"

                        info_about_lesson = {"homework": "Домашнего задания нет", "type": type_lesson}

                        if schedule.get(date) is None:
                            schedule[date] = [{lesson_name: info_about_lesson}]
                        else:
                            schedule[date].append({lesson_name: info_about_lesson})

        with open("databases/schedule.json", 'w', encoding='utf-8') as file_schedule:
            json.dump(schedule, file_schedule, ensure_ascii=False, indent=4)