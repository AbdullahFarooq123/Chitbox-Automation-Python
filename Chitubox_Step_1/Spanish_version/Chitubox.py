import json
import time

import pyautogui
from pywinauto import keyboard
from pywinauto.application import Application
import os

resize_list = json.load(open('rules.json', 'r'))
settings = json.load(open('settings.json', 'r'))
folders_data = open('folders', 'a')
folders_reached = [line.replace('\n', '') for line in open('folders', 'r').readlines()]
stl_file_path = settings['stl_folder_path']
chitubox_path = settings['CHITUBOX_path']
select_all_option = settings['SELECT_ALL_SELECTED']
folders = {}
for entry in os.scandir(stl_file_path):
    if not entry.is_file() and entry.name not in folders_reached:
        folders[entry.name] = []
        for files in os.scandir(stl_file_path + f'{entry.name}'):
            if files.is_file():
                if not str(entry.name).split('_')[0].replace(' ', '').upper().strip() in str(files.name).replace('_',
                                                                                                                 ''). \
                        replace(' ', '').upper():
                    folders[entry.name].append(files.name)
sorted_files = {}
for folder in folders:
    sorted_files[folder] = {}
    for resize_value in resize_list:
        list_file = []
        mirror_file = []
        for file in folders[folder]:
            file_size = str(file).split('.')[0][-len(resize_value):].upper()
            resize_size = resize_value.upper()
            if resize_size == file_size:
                if 'MIRROR THIS' in str(file).upper():
                    mirror_file.append(file)
                else:
                    list_file.append(file)
        if not len(list_file) == 0:
            sorted_files[folder][resize_value + ' NO MIRROR'] = list_file
        if not len(mirror_file) == 0:
            sorted_files[folder][resize_value + ' MIRROR'] = mirror_file

print(json.dumps(sorted_files, indent=4))


def mirror(file_size: int):
    mirror_location = (0.013 * Size.width, 0.56 * Size.height)
    click_element(mirror_location)
    x_mirror_location = (0.07 * Size.width, 0.56 * Size.height)
    click_element(x_mirror_location)
    time.sleep(file_size)


def click_element(points: tuple):
    pyautogui.moveTo(points[0], points[1])
    time.sleep(1)
    pyautogui.click()


def select_all():
    select_all_location = (Size.width * 0.95, Size.height * 0.16)
    if not select_all_option:
        pyautogui.moveTo(select_all_location[0], select_all_location[1])
        pyautogui.click()


def create_new_project():
    options = (Size.width * 0.02, Size.height * 0.034)
    click_element(options)
    new_project = app.CHITUBOX.child_window(title="New Project", control_type="MenuItem").wrapper_object()
    new_project.click_input()


def load_files(file_name: str, path: str):
    open_file_location = (Size.width * 0.07, Size.height * 0.04)
    click_element(open_file_location)
    text_field = app.CHITUBOX.child_window(title="Filnamn:", auto_id="1148", control_type="ComboBox").wrapper_object()

    text_field.click_input()
    keyboard.send_keys(path, with_spaces=True, pause=0)
    keyboard.send_keys('{ENTER}')
    keyboard.send_keys(file_name, with_spaces=True, pause=0)
    keyboard.send_keys('{ENTER}')
    time.sleep(3)


def auto_layout_selected(sleep: float):
    auto_layout = (Size.width * 0.30, Size.height * 0.047)
    autolayout_center = (Size.width * 0.31, Size.height * 0.101)
    click_element(auto_layout)
    time.sleep(0.5)
    click_element(autolayout_center)
    time.sleep(sleep)


def scale_selected(value: str, sleep: float):
    scale = (Size.width * 0.013, Size.height * 0.5)
    x_scale_percent = (Size.width * 0.104, Size.height * 0.51)
    click_element(scale)
    time.sleep(0.5)
    click_element(x_scale_percent)
    keyboard.send_keys(value, with_spaces=True, pause=0)
    time.sleep(sleep)


def save_project(path: str, file_length: int):
    save_project_location = (Size.width * 0.104, Size.height * 0.05)
    click_element(save_project_location)
    time.sleep(1)
    keyboard.send_keys(path, with_spaces=True, pause=0)
    keyboard.send_keys('{ENTER}')
    time.sleep(file_length)


def delete_all():
    delete_all_location = (Size.width * 0.975, Size.height * 0.16)
    click_element(delete_all_location)


def click_away():
    away_points = (Size.width * 0.11, Size.height * 0.194)
    click_element(away_points)


app = Application(backend='uia').start(chitubox_path).connect(title='CHITUBOX', timeout=1000)
time.sleep(5)
# app = Application(backend='uia').connect(title='CHITUBOX', timeout=1000)
Size = pyautogui.size()
select_all()
for folder in sorted_files:
    for sized in sorted_files[folder]:
        no_of_files = 0
        files_list = sorted_files[folder][sized]
        while no_of_files <= len(files_list):
            files = files_list[no_of_files:no_of_files + 15]
            click_away()
            create_new_project()
            for file in files:
                file = str(file).replace('(', '{(}').replace(')', '{)}').replace('+', '{+}').replace('-',
                                                                                                     '{-}').replace('^',
                                                                                                                    '{^}').replace(
                    '%', '{%}')
                load_files(file_name=file, path=f'{stl_file_path}{folder}\\')
            time.sleep(len(files_list))
            scale_selected(resize_list[sized.replace(' NO MIRROR', '').replace(' MIRROR', '')], len(files))
            auto_layout_selected(len(files) * 0.5)
            if "MIRROR" in str(files):
                mirror(len(files))
            save_project(
                f'{stl_file_path}{folder}\\{folder} {no_of_files + 1}_{no_of_files + 16} {resize_list[sized.replace(" NO MIRROR", "").replace(" MIRROR", "")]}{"{%}"} {"MIRROR" if "MIRROR" in str(files) else "NO MIRROR"}.chitubox',
                len(files))
            delete_all()
            no_of_files += 15
    folders_data.write(folder + '\n')
folders_data.close()
