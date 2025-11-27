import json

from datetime import date

import helpers_libs.weeks_operations as wk

now_day = date.today().day
now_month = date.today().month
now_year = date.today().year

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
        with open("databases/user_data.json", "r", encoding="utf-8") as data_file:
            all_users_date = json.load(data_file)
        all_users_date = create_new_user_info(username, all_users_date)
    except FileNotFoundError:
        create_file = open("databases/user_data.json", "w", encoding="utf-8")
        create_file.close()
        all_users_date = create_new_user_info(username, {})
    with open("databases/user_data.json", "w", encoding="utf-8") as data_file:
        json.dump(all_users_date, data_file, ensure_ascii=False, indent=4)
    return all_users_date[username]


def data_update(username, **kwargs):
    with open("databases/user_data.json", "r", encoding="utf-8") as data_file:
        all_users_date = json.load(data_file)
    current_user_info = all_users_date[username]
    for old_info in kwargs:
        current_user_info[old_info] = kwargs[old_info]
    all_users_date[username] = current_user_info
    with open("databases/user_data.json", "w", encoding="utf-8") as data_file:
        json.dump(all_users_date, data_file, ensure_ascii=False, indent=4)

    return current_user_info


def update_values(username):
    wk.current_day, wk.current_month, wk.current_year = data_update(username,
                                                           current_day=wk.current_day,
                                                           current_month=wk.current_month,
                                                           current_year=wk.current_year).values()
    return