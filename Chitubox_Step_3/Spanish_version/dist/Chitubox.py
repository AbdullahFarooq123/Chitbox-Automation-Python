import json
import time

import pyautogui
from pywinauto import keyboard
from pywinauto.application import Application
import os
import shutil

settings = json.load(open('C:\\SKRIPT\\Chitubox Script 3 slice\\settings.json', 'r'))
rules = json.load(open('C:\\SKRIPT\\Chitubox Script 3 slice\\rules.json', 'r'))
files_path = settings["folder_path"]
chitubox_old_path = settings["CHITUBOX_path_old"]
chitubox_new_path = settings["CHITUBOX_path_new"]
select_all_option = settings["SELECT_ALL_SELECTED"]
old_software_rules = rules["software_rules"]["old"]
new_software_rules = rules["software_rules"]["new"]
old_machine_rules = rules["machine_rules"]["old"]
new_machine_rules = rules["machine_rules"]["new"]
old_clicks_locations = rules["clicks_locations"]["old"]
new_clicks_locations = rules["clicks_locations"]["new"]


def search_for_chitubox_file():
    chitubox_files_old = {}
    chitubox_files_new = {}
    for entry in os.scandir(files_path):
        if entry.is_file() and str(entry.name).endswith('.chitubox'):
            for rule in old_software_rules:
                if rule.upper() in entry.name.upper():
                    if rule not in chitubox_files_old:
                        chitubox_files_old[rule] = []
                    chitubox_files_old[rule].append(entry.name)
            for rule in new_software_rules:
                if rule.upper() in entry.name.upper():
                    if rule not in chitubox_files_new:
                        chitubox_files_new[rule] = []
                    chitubox_files_new[rule].append(entry.name)
    return {
        "old": chitubox_files_old,
        "new": chitubox_files_new
    }


def click_element(points: tuple):
    pyautogui.moveTo(points[0], points[1])
    time.sleep(1)
    pyautogui.click()


def select_all(select_all_location):
    if not select_all_option:
        click_element(select_all_location)


def create_new_project():
    options = (Size.width * 0.02, Size.height * 0.034)
    click_element(options)
    new_project = app.CHITUBOX.child_window(title="New Project", control_type="MenuItem").wrapper_object()
    new_project.click_input()


def load_files(file_name: str, path: str):
    open_file_location = (Size.width * 0.07, Size.height * 0.04)
    click_element(open_file_location)
    text_field = app.CHITUBOX.child_window(title="Filnamn:", auto_id="1148",
                                           control_type="ComboBox").wrapper_object()

    text_field.click_input()
    keyboard.send_keys(path, with_spaces=True, pause=0)
    keyboard.send_keys('{ENTER}')
    time.sleep(5)
    keyboard.send_keys(file_name, with_spaces=True, pause=0)
    keyboard.send_keys('{ENTER}')
    time.sleep(3)


def save_project(path: str, file_length: float, save_project_location):
    click_element(save_project_location)
    time.sleep(1)
    keyboard.send_keys(path, with_spaces=True, pause=0)
    keyboard.send_keys('{ENTER}')
    time.sleep(file_length)


def delete_all(delete_all_location):
    click_element(delete_all_location)


def click_away():
    away_points = (Size.width * 0.11, Size.height * 0.194)
    click_element(away_points)


def str_to_tuple(string_coordinates: str):
    values = string_coordinates.split(',')
    return Size.width * float(values[0]), Size.height * float(values[1])


def refactor_for_send_keys(name: str):
    return name.replace('(', '{(}').replace(')', '{)}').replace('+', '{+}').replace('-',
                                                                                    '{-}').replace('^',
                                                                                                   '{^}').replace(
        '%', '{%}')


Size = pyautogui.size()
chitubox_files = search_for_chitubox_file()
old_software_files = chitubox_files['old']
new_software_files = chitubox_files['new']
close_coordinates = (Size.width * 0.98, Size.height * 0.008)
print(chitubox_files)
exit(1)
if len(old_software_files) > 0:
    app = Application(backend='uia').start(chitubox_old_path).connect(title='CHITUBOX', timeout=1000)
    time.sleep(5)
    select_all(str_to_tuple(old_clicks_locations["select_all"]))
    click_element(str_to_tuple(old_clicks_locations["updates_close"]))

    for rule in old_software_files:
        for file in old_software_files[rule]:
            click_away()
            load_files(file_name=refactor_for_send_keys(file), path=refactor_for_send_keys(files_path))
            size = float(os.stat(files_path + file).st_size) / (1024 * 1024)
            time.sleep(size / 30)
            click_element(str_to_tuple(old_clicks_locations["settings"]))
            values = str(old_machine_rules[rule]).split(' > ')

            machine_name = values[0]
            profile_name = values[1]
            click_element(str_to_tuple(old_clicks_locations[machine_name]))
            click_element(str_to_tuple(old_clicks_locations["profiles"]))
            click_element(str_to_tuple(old_clicks_locations[profile_name]))
            click_element(str_to_tuple(old_clicks_locations["settings_close"]))
            click_element(str_to_tuple(old_clicks_locations["slice"]))
            click_element(str_to_tuple(old_clicks_locations["out_of_bounds"]))
            time.sleep(size / 10)
            click_element(str_to_tuple(old_clicks_locations["save_cfg"]))
            click_element(str_to_tuple(old_clicks_locations["save_cfg" if not "Flash" in machine_name else "other_save_cfg"]))
            save_project(files_path + str(file).replace('.chitubox', ''), size / 10,
                         str_to_tuple(old_clicks_locations["save_cfg"]))
            click_element(str_to_tuple(old_clicks_locations["back"]))
            click_element(str_to_tuple(old_clicks_locations["delete_all"]))
            print(f'File : {file} completed!')
    click_element(close_coordinates)
if len(new_software_files) > 0:
    app = Application(backend='uia').start(chitubox_new_path).connect(title='CHITUBOX', timeout=1000)
    time.sleep(5)
    select_all(str_to_tuple(new_clicks_locations["select_all"]))
    click_element(str_to_tuple(new_clicks_locations["updates_close"]))
    for rule in new_software_files:
        for file in new_software_files[rule]:
            click_away()
            load_files(file_name=refactor_for_send_keys(file), path=refactor_for_send_keys(files_path))
            size = float(os.stat(files_path + file).st_size) / (1024 * 1024)
            time.sleep(size / 15)
            click_element(str_to_tuple(new_clicks_locations["settings"]))
            values = str(new_machine_rules[rule]).split(' > ')
            machine_name = values[0]
            profile_name = values[1]
            click_element(str_to_tuple(new_clicks_locations[machine_name]))
            click_element(str_to_tuple(new_clicks_locations["profiles"]))
            click_element(str_to_tuple(new_clicks_locations[profile_name]))
            click_element(str_to_tuple(new_clicks_locations["settings_close"]))
            click_element(str_to_tuple(new_clicks_locations["slice"]))
            click_element(str_to_tuple(new_clicks_locations["out_of_bounds"]))
            sleep_time = size / 5 if not 'M3' in new_clicks_locations[
                machine_name] else size
            time.sleep(sleep_time/30)
            print(machine_name)
            click_element(str_to_tuple(new_clicks_locations["other_save_cfg" if "Phrozen Sonic Mini 8K" in machine_name or "AnyCubic Photon M3 Max" in machine_name else "save_cfg"]))
            save_project(files_path + str(file).replace('.chitubox', ''), sleep_time + (sleep_time if "AnyCubic Photon M3 Max" in machine_name else 0),
                         str_to_tuple(new_clicks_locations["save_cfg"]))
            click_element(str_to_tuple(new_clicks_locations["back"]))
            click_element(str_to_tuple(new_clicks_locations["delete_all"]))
            print(f'File : {file} completed!')

    click_element(close_coordinates)
input('Process Done. Press "Enter" to exit!')
