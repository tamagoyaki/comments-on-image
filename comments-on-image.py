'''
This is designed for python3.8 since ubuntu 22.04 has set python3.8 as default.

  Write comments on image you are viewing. These comments are saved to CSV file.


  USAGE

    $ python comments-on-image.py

  DIRECTORY STRUCTUR

    cam number/filename  (ex, 1/image0001.jpg)

    For Example)
        .
        ├── 1
        │   ├── IMAG0001.JPG
        │   └── IMAG0002.JPG
        ├── 2
        │   ├── IMAG0001.JPG
        │   └── IMAG0002.JPG
        ├── comments-on-image.py
        ├── temp
        │   ├── 1
        │   │   ├── IMAG0001.PNG
        │   │   └── IMAG0002.PNG
        │   └── 6
        │       ├── IMAG1315.PNG
        │       ├── IMAG1316.PNG
        │       └── IMAG1317.PNG
        └── info.csv

        The temp directory made by this script is used for temporaly as cache.

    WARNING:

        The cache is not updated even if the source image is updated. :-P

'''
import os
import csv
import glob
import PySimpleGUI as sg
from PIL import Image
from exif import Image as ExImage
from datetime import datetime

# info CSV
#
#   FORMAT
#
#     source filename, camera number, filename, date, remark, remark, remark
#
csvfilename = "info.csv"

try:
    with open(csvfilename) as f:
        l = csv.reader(f)
        dcsv = {row[0]: row for row in l}
except OSError:
    dcsv = {}

# list all JPG
jpgs = glob.glob('**/*.JPG', recursive=True)

# Window Layout
layout = [
    [sg.Image(key='image')],
    [sg.Text('rem1:'), sg.InputText(key='rem1', size=(4, 4)),
     sg.Text('rem2:'), sg.InputText(key='rem2', size=(4, 4)),
     sg.Text('rem3:'), sg.InputText(key='rem3'),
     sg.Button('prev', key='prev'), sg.Button('next', key='next'),
    ],
]
window = sg.Window("Edit info", layout, finalize=True, location=(200, 200),
                   keep_on_top=True)

# one jpg at a time
ix = 0
while True:
    jpg = jpgs[ix]
    exif = ExImage(jpg)
    timestamp = datetime.strptime(exif.datetime,
                                  "%Y:%m:%d %H:%M:%S").strftime(
                                      "%Y/%m/%d %H:%M:%S")
    png = 'temp/' + jpg.replace("JPG", "PNG")
    camnumber = jpg.split('/')[0]
    filename = os.path.basename(jpg)

    # Create PNG in temporaly directory since PySimpleGUI only supports PNG
    # and GIF
    if os.path.exists(png) is False:
        img = Image.open(jpg)
        img.thumbnail((640, 640))

        os.makedirs(os.path.dirname(png), exist_ok=True)
        img.save(png)

    # current info from CSV
    try:
        info = dcsv[jpg]
    except KeyError:
        info = [''] * 7

    # show image and info then wait an event occurs
    window['image'].update(filename=png)
    window['rem1'].update(info[4])
    window['rem2'].update(info[5])
    window['rem3'].update(info[6])

    event, values = window.read()
    if event == 'prev' or event == 'next' or event == sg.WIN_CLOSED:
        rem1 = values['rem1'] if values else ''
        rem2 = values['rem2'] if values else ''
        rem3 = values['rem3'] if values else ''

        print(f"camnumber={camnumber}, filename={filename}, {timestamp} "
              f"rem1={rem1}, rem2={rem2}, rem3={rem3}")

        info[0] = jpg
        info[1] = camnumber
        info[2] = filename
        info[3] = timestamp.split(' ')[0]
        info[4] = rem1
        info[5] = rem2
        info[6] = rem3
        dcsv[jpg] = info

        if event == 'next':
            ix += 1
            if ix == len(jpgs):
                ix = 0

        if event == 'prev':
            ix -= 1
            if 0 > ix:
                ix = len(jpgs) -1

        if event == sg.WIN_CLOSED:
            break

# write CSV
with open(csvfilename, 'w') as f:
    writer = csv.writer(f)
    for key, val in dcsv.items():
        writer.writerow(val)

window.close()
