"""
Uses DeOldify AI Image Colorization Software's API to color a given image
"""

import os
import sys
import io
import json
import wget
import requests
import PySimpleGUI as sg
from PIL import Image, ImageTk


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_img_data(img_url, maxsize=(600, 600), first=False):
    """Generate image data using PIL"""
    img = Image.open(img_url)
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)

# setup request elements
headers = {'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K',}
files = {'image': '',}
with open(resource_path('API-KEY.json'), 'r') as file:
    headers = json.load(file)

# setup gui layout
sg.theme('LightGrey1')
image_elem = sg.Image(resource_path('placeholder.gif'))
layout = [[sg.Text('DeOldify - An AI that can colorize and restore old images and footage')],
          [sg.Button('Select Image'), sg.Button('Process'), sg.Button('Close')],
          [sg.Text('API Key'), sg.InputText(headers['api-key']), sg.Button('Set')],
          [image_elem]]

# Create the Window
window = sg.Window('DeOldify', layout, resizable=True)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read() # blovking function till user interacts with anything

    if event in (None, 'Close'):	# if user closes window or clicks cancel
        break

    if event == 'Select Image':
        image = sg.popup_get_file('Image file to open', default_path='./')
        if not image:
            sg.popup_cancel('Failed collecting image, please retry')
        else:
            image_elem.update(data=get_img_data(image))
            files['image'] = (image, open(image, 'rb'))
            print(image)

    elif event == 'Process':
        sg.popup("Working")
        response = requests.post('https://api.deepai.org/api/colorizer',
                                 headers=headers, files=files)
        response_dict = json.loads(response.text)
        print(response.content)
        if 'output_url' in response_dict:
            url = sg.popup_get_folder('Save Image to', default_path='./')
            image = wget.download(str(response_dict['output_url']), out=url)
            image_elem.update(data=get_img_data(image))
            sg.popup("Done")
        else:
            sg.popup("Failed: Check console")

    elif event == 'Set':
        headers['api-key'] = str(values[0])
        with open(resource_path('API-KEY.json'), 'w') as file:
            json.dump(headers, file)

window.close()
