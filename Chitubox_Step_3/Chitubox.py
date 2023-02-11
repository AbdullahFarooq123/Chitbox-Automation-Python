import json
import time

import pyautogui
from PIL import Image
from pywinauto import keyboard
from pywinauto.application import Application
import os
import cv2
import numpy

settings = json.load(open('settings.json', 'r'))
rules = json.load(open('rules.json', 'r'))
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
    text_field = app.CHITUBOX.child_window(title="File name:", auto_id="1148",
                                           control_type="ComboBox").wrapper_object()

    text_field.click_input()
    keyboard.send_keys(path, with_spaces=True, pause=0)
    keyboard.send_keys('{ENTER}')
    time.sleep(5)
    keyboard.send_keys(file_name, with_spaces=True, pause=0)
    keyboard.send_keys('{ENTER}')
    time.sleep(3)


def save_project(path: str, file_length: float, save_format: str):
    time.sleep(1)
    keyboard.send_keys(path, with_spaces=True, pause=0)
    time.sleep(1)
    click_element((500, 7))
    # file_name_box = app.CHITUBOX.child_window(title="File name:", auto_id="1001", control_type="Edit").wrapper_object()
    # file_dilogue = app.CHITUBOX.child_window(title="Save Slicer", control_type="Window").wrapper_object()
    # file_dilogue.click_input()
    # file_name_box.click_input()
    if not len(save_format) == 0:
        file_type_box = app.CHITUBOX.child_window(title="Save as type:", auto_id="FileTypeControlHost",
                                                  control_type="ComboBox").wrapper_object()
        file_type_box.click_input()
        if save_format == 'fdg':
            fdg_format = app.CHITUBOX.child_window(title="fdg(*.fdg)", control_type="ListItem").wrapper_object()
            fdg_format.click_input()
    save_btn = app.CHITUBOX.child_window(title="Save", auto_id="1", control_type="Button").wrapper_object()
    save_btn.click_input()
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


def take_screenshot(left: float, right: float, upper: float, lower: float, slice=True):
    screenshot = pyautogui.screenshot()
    screenshot.save(f'screen shot.png')
    if slice:
        img = Image.open(f'screen shot.png')
        screenshot_width = img.width
        screenshot_height = img.height
        left = screenshot_width - int(screenshot_width * left)
        right = int(screenshot_width * right)
        upper = screenshot_height - int(screenshot_height * upper)
        lower = int(screenshot_height * lower)
        box = (left, upper, right, lower)
        img2 = img.crop(box)
        img2.save(f'screen shot.png')
    return os.getcwd() + '\\screen shot.png'


def match_screenshot(matching_img_path: str, image_path: str, threshold: float) -> tuple[bool, tuple]:
    matching_img = cv2.imread(matching_img_path, cv2.IMREAD_UNCHANGED)
    matching_img = cv2.cvtColor(numpy.array(matching_img), cv2.COLOR_RGB2BGR)
    threshold = threshold
    passed_screenshot = None
    screenshot = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    screenshot = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2BGR)
    result = cv2.matchTemplate(screenshot, matching_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        passed_screenshot = screenshot
    if passed_screenshot is not None:
        return True, max_loc
    else:
        return False, ()


def repeatedly_check_for_screenshot(matching_img_path: str, threshold: float, left: float, right: float, upper: float,
                                    lower: float, invert_condition=False):
    matching_img = cv2.imread(matching_img_path, cv2.IMREAD_UNCHANGED)
    matching_img = cv2.cvtColor(numpy.array(matching_img), cv2.COLOR_RGB2BGR)
    while True:
        path = take_screenshot(left, right, upper, lower)
        threshold = threshold
        passed_screenshot = None
        screenshot = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        screenshot = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(screenshot, matching_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            passed_screenshot = screenshot
        if (passed_screenshot is None) if not invert_condition else (passed_screenshot is not None):
            break
        time.sleep(0.5)


Size = pyautogui.size()
chitubox_files = search_for_chitubox_file()
old_software_files = chitubox_files['old']
new_software_files = chitubox_files['new']
print(chitubox_files)
close_coordinates = (Size.width * 0.98, Size.height * 0.008)
if len(old_software_files) > 0:
    # app = Application(backend='uia').start(chitubox_old_path).connect(title='CHITUBOX', timeout=1000)
    app = Application(backend='uia').connect(title='CHITUBOX', timeout=1000)

    time.sleep(5)
    # path = take_screenshot(left=0.677, right=0.677, upper=0.7685, lower=0.37)
    # if match_screenshot(os.getcwd() + '\\images\\check_for_updates.png', path, 0.9)[0]:
    #     click_element(str_to_tuple(old_clicks_locations["updates_close"]))
    # path = take_screenshot(left=0.10, right=1, upper=0.879, lower=0.212)
    # if match_screenshot(os.getcwd() + '\\images\\select_all_unchecked.png', path, 0.9)[0]:
    #     click_element(str_to_tuple(old_clicks_locations["select_all"]))
    for rule in old_software_files:
        for file in old_software_files[rule]:
            size = float(os.stat(files_path + file).st_size) / (1024 * 1024)
            # click_away()
            # load_files(file_name=refactor_for_send_keys(file), path=refactor_for_send_keys(files_path))
            # time.sleep(size * 0.1)
            # repeatedly_check_for_screenshot(os.getcwd() + '\\images\\loading_file.png', 0.6, 1, 1, 0.08, 0.96)
            # click_element(str_to_tuple(old_clicks_locations["settings"]))
            # values = str(old_machine_rules[rule]).split(' > ')
            #
            # machine_name = values[0]
            # profile_name = values[1]
            # click_element(str_to_tuple(old_clicks_locations[machine_name]))
            # click_element(str_to_tuple(old_clicks_locations["profiles"]))
            # click_element(str_to_tuple(old_clicks_locations[profile_name]))
            # click_element(str_to_tuple(old_clicks_locations["settings_close"]))
            # click_element(str_to_tuple(old_clicks_locations["slice"]))
            # time.sleep(1)
            # path = take_screenshot(left=0.65,
            #                        right=0.65,
            #                        upper=0.62,
            #                        lower=0.57, )
            # if match_screenshot(os.getcwd() + '\\images\\out_of_bounds.png', path, 0.6)[0]:
            #     click_element(str_to_tuple(old_clicks_locations["out_of_bounds"]))
            # time.sleep(size * 0.1)
            # repeatedly_check_for_screenshot(os.getcwd() + '\\images\\slicing.png', 0.3, 1, 1, 0.08, 0.96)
            path = take_screenshot(left=0.14, right=1, upper=0.60, lower=0.65, slice=False)
            location = match_screenshot(os.getcwd() + '\\images\\save_btn.png', path, 0.9)[1]
            click_element(location)
            save_project(files_path + str(file).replace('.chitubox', ''), size * 0.1,
                         'fdg' if 'Flash_' == rule else '')
            repeatedly_check_for_screenshot(os.getcwd() + '\\images\\writing_file.png', 0.5, 1, 1, 0.08, 0.96)
            click_element(str_to_tuple(old_clicks_locations["back"]))
            time.sleep(1)
            click_element(str_to_tuple(old_clicks_locations["delete_all"]))
            time.sleep(1)
            print(f'File : {file} completed!')
    click_element(close_coordinates)
if len(new_software_files) > 0:
    app = Application(backend='uia').start(chitubox_new_path).connect(title='CHITUBOX', timeout=1000)
    time.sleep(8)
    path = take_screenshot(left=0.677, right=0.677, upper=0.7685, lower=0.37)
    if match_screenshot(os.getcwd() + '\\images\\check_for_updates.png', path, 0.9)[0]:
        click_element(str_to_tuple(new_clicks_locations["updates_close"]))
    path = take_screenshot(left=0.10, right=1, upper=0.879, lower=0.212)
    if match_screenshot(os.getcwd() + '\\images\\select_all_unchecked.png', path, 0.9)[0]:
        click_element(str_to_tuple(new_clicks_locations["select_all"]))
    for rule in new_software_files:
        for file in new_software_files[rule]:
            size = float(os.stat(files_path + file).st_size) / (1024 * 1024)
            click_away()
            load_files(file_name=refactor_for_send_keys(file), path=refactor_for_send_keys(files_path))
            time.sleep(size * 0.1)
            repeatedly_check_for_screenshot(os.getcwd() + '\\images\\loading_file.png', 0.6, 1, 1, 0.08, 0.96)
            click_element(str_to_tuple(new_clicks_locations["settings"]))
            values = str(new_machine_rules[rule]).split(' > ')
            machine_name = values[0]
            profile_name = values[1]
            click_element(str_to_tuple(new_clicks_locations[machine_name]))
            click_element(str_to_tuple(new_clicks_locations["profiles"]))
            click_element(str_to_tuple(new_clicks_locations[profile_name]))
            click_element(str_to_tuple(new_clicks_locations["settings_close"]))
            click_element(str_to_tuple(new_clicks_locations["slice"]))
            time.sleep(1)
            path = take_screenshot(left=0.65,
                                   right=0.65,
                                   upper=0.62,
                                   lower=0.57, )
            if match_screenshot(os.getcwd() + '\\images\\out_of_bounds.png', path, 0.6)[0]:
                click_element(str_to_tuple(new_clicks_locations["out_of_bounds"]))
            time.sleep(size * 0.1)
            repeatedly_check_for_screenshot(os.getcwd() + '\\images\\slicing.png', 0.3, 1, 1, 0.08, 0.96)
            path = take_screenshot(left=0.14, right=1, upper=0.60, lower=0.65, slice=False)
            location = match_screenshot(os.getcwd() + '\\images\\save_btn.png', path, 0.8)[1]
            click_element(location)
            save_project(files_path + str(file).replace('.chitubox', ''), size * 0.1,
                         '')
            repeatedly_check_for_screenshot(os.getcwd() + '\\images\\writing_file.png', 0.5, 1, 1, 0.08, 0.96)
            time.sleep(2)
            repeatedly_check_for_screenshot(os.getcwd() + '\\images\\write_successful_open_folder.png', 0.8, 1, 1, 0.08,
                                            0.96, invert_condition=True)
            click_element(str_to_tuple(new_clicks_locations["back"]))
            time.sleep(1)
            click_element(str_to_tuple(new_clicks_locations["delete_all"]))
            time.sleep(1)
            print(f'File : {file} completed!')

    click_element(close_coordinates)
input('Process Done. Press "Enter" to exit!')
