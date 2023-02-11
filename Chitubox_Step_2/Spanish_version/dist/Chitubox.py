import json
import time

import pyautogui
from pywinauto import keyboard
from pywinauto.application import Application
import os
import shutil


def compare_and_copy(lookup_file, txt_filename, extension: str, source: str, destination: str, file_size: str,
                     include_underscore,
                     save=False, copy=True):
    global file_match
    global copy_info
    if str(lookup_file.name).endswith(extension):
        lookup_filename = remove_characters(lookup_file.name.replace(file_size, ''), include_underscore).replace(
            extension, '').strip()
        txt_file_name = remove_characters(txt_filename, include_underscore).replace('.txt', '').strip()
        if False:
            with open('C:\\SKRIPT\\Chitubox skript 2 find\\debug.txt', 'a', encoding='utf-8') as debug_file:
                debug_file.write(f'{lookup_file.name} ({lookup_filename}) : {txt_filename} ({txt_file_name})\n')
        if compare_files(lookup_filename.upper(), txt_file_name.upper(), lookup_file.name, txt_filename, save):

            if copy:
                new_copy_name = lookup_file.name.replace(extension, f' {file_size}') + extension
                shutil.copy(src=source, dst=destination + new_copy_name)
                copy_info.append(f'Copied from {source} -TO- {destination} : {new_copy_name}')
            return True

    return False


def compare_files(file_1: str, file_2: str, original_1, original_2, save=True):
    global file_match
    match = 0
    smaller_length = len(file_1) if len(file_1) >= len(file_2) else len(file_2)
    for file_1_char, file_2_char in zip(file_1, file_2):
        if file_1_char == file_2_char:
            match += 1
    match_percentage = round((match / smaller_length) * 100)
    if save and match_percentage == 100:
        file_match[f'{original_1} - {original_2}'] = match_percentage
    return match_percentage == 100


def remove_characters(filename: str, include_underscore: bool):
    underscore = ''
    if filename[0] == '_' and include_underscore:
        underscore = '_'
    special_characters = ['~', '`', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '=', '{', '[', ']',
                          '}', ';', ':', "'", ',', '?', '_', ' ', 'sup', 'SUP', 'vh', 'VH', 'supported', 'SUPPORTED',
                          'Supported', 'support', 'SUPPORt', 'Support']
    for char in special_characters:
        filename = filename.replace(char, '')
    return underscore + filename.strip()


def search_for_txt_file(file_path: str):
    text_files = []
    for entry in os.scandir(file_path):
        if entry.is_file() and str(entry.name).endswith('.txt'):
            text_files.append(entry.name)
        elif not entry.is_file():
            files = search_for_txt_file(f'{file_path + entry.name}\\')
            if not len(files) == 0:
                folders_with_txt[entry.name] = {
                    'Path': file_path,
                    'Files': files
                }
    return text_files


def search_for_chitubox_and_stl(lookup_path, txt_filename, stl_file_path, folder, txt_file_size, extension):
    found = False
    for entry in os.scandir(lookup_path):
        if entry.is_file():
            found = compare_and_copy(entry, txt_filename, extension, lookup_path + f'\\{entry.name}',
                                     stl_file_path + f'{folder}\\', txt_file_size, True)
        elif not entry.is_file():
            search_for_chitubox_and_stl(lookup_path + f'\\{entry.name}', txt_filename, stl_file_path, folder,
                                        txt_file_size, extension)
    return found


def search_for_resize(resize_path, txt_filename_only, stl_file_path, folder, txt_file_size, resize_to,
                      txt_filename_full):
    chitubox_found = False
    sup_found = False
    for entry in os.scandir(resize_path):
        if entry.is_file():
            chitubox_found = compare_and_copy(lookup_file=entry,
                                              txt_filename=txt_filename_only,
                                              extension='.chitubox',
                                              source=resize_path + f'\\{entry.name}',
                                              destination=stl_file_path + f'{folder}\\', file_size=txt_file_size,
                                              include_underscore=True,
                                              save=False,
                                              copy=True)
        else:
            search_for_resize(resize_path + f'{entry.name}\\', txt_filename_only, stl_file_path, folder, txt_file_size,
                              resize_to, txt_filename_full)
    if not chitubox_found:
        for entry in os.scandir(resize_path):
            if entry.is_file():
                if compare_and_copy(lookup_file=entry,
                                    txt_filename=txt_filename_only,
                                    extension='.stl',
                                    source=resize_path + f'\\{entry.name}',
                                    destination=stl_file_path + f'{folder}\\', file_size=txt_file_size,
                                    include_underscore=False,
                                    save=True,
                                    copy=False) and (
                        'sup' in entry.name.lower() or 'supported' in entry.name.lower() or 'support' in entry.name.lower()):
                    sup_found = True
            else:
                search_for_resize(resize_path + f'{entry.name}\\', txt_filename_only, stl_file_path, folder,
                                  txt_file_size,
                                  resize_to, txt_filename_full)
    if sup_found:
        files = []
        for entry in os.scandir(resize_path):
            if entry.is_file():
                if (
                        'sup' in entry.name.lower() or 'supported' in entry.name.lower() or 'support' in entry.name.lower()) and not str(
                        entry.name).startswith('_') and str(entry.name).endswith('.stl'):
                    files.append(entry.name)
        if not len(files) == 0:
            new_name = txt_filename_full.replace('.txt', '.chitubox')
            if not str(new_name).startswith('_'):
                new_name = '_' + new_name
            resize_files[resize_path] = {'Old Names': files,
                                         'New Name': new_name,
                                         'Copy From': resize_path,
                                         'Copy To': stl_file_path + f'{folder}\\',
                                         'Resize To': resize_to
                                         }


file_match = {}
copy_info = []
sizes = json.load(open('C:\\SKRIPT\\Chitubox skript 2 find\\sizes.json', 'r'))
settings = json.load(open('C:\\SKRIPT\\Chitubox skript 2 find\\settings.json', 'r'))
folders_data = open('folders', 'a')
folders_reached = [line.replace('\n', '') for line in open('folders', 'r').readlines()]
stl_file_path = settings['stl_folder_path']
chitubox_path = settings['CHITUBOX_path']
select_all_option = settings['SELECT_ALL_SELECTED']
lookup_paths = settings['Lookup_paths']
resize_paths = settings['Resize_paths']
folders_with_txt = {}
resize_files = {}
print(f'Looking for .txt in {stl_file_path}')
print('Please wait......\n')
search_for_txt_file(stl_file_path)
print('txt files found : \n')
print(json.dumps(folders_with_txt, indent=4))
print()
print('Looking for matching files')
print('Please wait...')
for folder in folders_with_txt:
    for txt_file in folders_with_txt[folder]['Files']:
        txt_filename_only = str(txt_file)
        txt_file_size = ''
        for size in sizes:
            if size.upper() == txt_filename_only.split('.')[0][-len(size):].upper():
                txt_filename_only = txt_filename_only.replace(size, '')
                txt_file_size = size
                break
        found_stl = False
        found_chitubox = False
        for lookup_path in lookup_paths:
            found_chitubox = search_for_chitubox_and_stl(folder=folder,
                                                         lookup_path=lookup_path,
                                                         txt_filename=txt_filename_only,
                                                         stl_file_path=stl_file_path,
                                                         txt_file_size=txt_file_size,
                                                         extension='.chitubox')
        if not found_chitubox:
            for lookup_path in lookup_paths:
                found_stl = search_for_chitubox_and_stl(folder=folder,
                                                        lookup_path=lookup_path,
                                                        txt_filename=txt_filename_only,
                                                        stl_file_path=stl_file_path,
                                                        txt_file_size=txt_file_size,
                                                        extension='.stl')
        if not found_stl:
            for resize_path in resize_paths:
                search_for_resize(resize_path=resize_path,
                                  txt_filename_only=txt_filename_only,
                                  stl_file_path=stl_file_path,
                                  folder=folder,
                                  txt_file_size=txt_file_size,
                                  resize_to=resize_paths[resize_path],
                                  txt_filename_full=txt_file)
print('Files Found for resize\n')
print(json.dumps(resize_files, indent=4))
print('\n')
print('File Matches : \n')
sorted_ = sorted(file_match.items(), key=lambda kv: (kv[1], kv[0]))
for pair in sorted_:
    print(pair)
print('\n')
print('Copy Info : \n')
for info in copy_info:
    print(info)


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
    text_field = app.CHITUBOX.child_window(title="Filnamn:", auto_id="1148",
                                           control_type="ComboBox").wrapper_object()

    text_field.click_input()
    keyboard.send_keys(path, with_spaces=True, pause=0)
    keyboard.send_keys('{ENTER}')
    time.sleep(5)
    keyboard.send_keys(file_name, with_spaces=True, pause=0)
    keyboard.send_keys('{ENTER}')
    time.sleep(3)


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


def refactor_for_send_keys(name: str):
    return name.replace('(', '{(}').replace(')', '{)}').replace('+', '{+}').replace('-',
                                                                                    '{-}').replace('^',
                                                                                                   '{^}').replace(
        '%', '{%}')


if not len(resize_files) == 0:
    print('\nResize Copy : \n')
    app = Application(backend='uia').start(chitubox_path).connect(title='CHITUBOX', timeout=1000)
    time.sleep(5)
    Size = pyautogui.size()
    select_all()
    for path in resize_files:
        refactored_load_path = refactor_for_send_keys(path)
        refactored_new_file_name = refactor_for_send_keys(resize_files[path]['New Name'])
        refactored_save_path = refactor_for_send_keys(resize_files[path]['Copy From'])
        click_away()
        create_new_project()
        for data in resize_files[path]['Old Names']:
            refactored_file_name = refactor_for_send_keys(data)
            load_files(path=refactored_load_path, file_name=refactored_file_name)
            time.sleep(3)
        scale_selected(resize_files[path]['Resize To'], 3)
        save_project(refactored_save_path + refactored_new_file_name, len(resize_files[path]['Old Names']) * 3)
        delete_all()
        shutil.copy(src=resize_files[path]['Copy From'] + resize_files[path]['New Name'],
                    dst=resize_files[path]['Copy To'] + resize_files[path]['New Name'])
        print(
            f'Copied From {resize_files[path]["Copy From"] + resize_files[path]["New Name"]} -TO- {resize_files[path]["Copy To"] + resize_files[path]["New Name"]}')
input('\nPress Enter to continue!')
