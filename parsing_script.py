import requests
import hashlib
import json

flag_read = False
falling_process = False

name_group = 'М8О-113БВ-25'

try:
    with open("schedule.json", "r", encoding='utf-8') as file_schedule:
        schedule = json.load(file_schedule)
    flag_read = True

except json.decoder.JSONDecodeError:
    pass

except FileNotFoundError:
    open("schedule.json", "w", encoding='utf-8')

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

        for i in parse_date.items():
            if i[0] != 'group':
                date = '-'.join(i[0].split('.')[::-1])
                if i[-1] != name_group:
                    for j in i[-1]["pairs"].values():
                        if schedule.get(date) is None:
                            schedule[date] = list(j.keys())
                        else:
                            schedule[date].append(*j.keys())

        with open("schedule.json", 'w', encoding='utf-8') as file_schedule:
            json.dump(schedule, file_schedule, ensure_ascii=False, indent=4)
