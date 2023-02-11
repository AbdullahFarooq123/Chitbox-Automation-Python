import time

import pynput.mouse as mouse_
import pynput.keyboard as keyboard_
import keyboard
import pyautogui


def print_clicks(x, y, button, pressed):
    global i, Size
    if pressed:
        print(x,y)
        print(f'Click {i} : ({x / Size.width}, {y / Size.height})')
        i += 1


def wait_for_key(to_stop: mouse_.Listener, key):
    global to_stop_loop
    to_stop_loop = True
    to_stop.stop()


i = 1
to_stop_loop = False
Size = pyautogui.size()
print('Press Enter to start registering click locations and press any key to exit')
keyboard.wait('enter')
listener_mouse = mouse_.Listener(on_click=print_clicks)
listener_mouse.start()
time.sleep(1)
listener_keyboard = keyboard_.Listener(on_press=lambda key: wait_for_key(listener_mouse, key))
listener_keyboard.start()
while not to_stop_loop:pass

