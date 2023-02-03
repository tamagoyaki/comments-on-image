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
import re
import csv
import glob
import PySimpleGUI as sg
from PIL import Image
from exif import Image as ExImage
from datetime import datetime

#
# info CSV
#
csvfilename = "info.csv"
headers = {
    # header : show
    'jpg': {'show': False, 'size': (4, 4), 'newline': False},
    'camnum': {'show': False, 'size': (4, 4), 'newline': False},
    'filename': {'show': False, 'size': (4, 4), 'newline': False},
    'timestamp': {'show': True, 'size': (16, 4), 'newline': True},
    'rem1': {'show': True, 'size': (4, 4), 'newline': False},
    'rem2': {'show': True, 'size': (4, 4), 'newline': True},
    'rem3': {'show': True, 'size': (4, 4), 'newline': True},
}

try:
    with open(csvfilename, encoding='shift_jis') as f:
        l = csv.reader(f)
        dcsv = {row[0]: row for row in l}
        lastkey = next(reversed(dcsv), None)
except OSError:
    dcsv = {}
    lastkey = ''

# list all JPG
jpgs = glob.glob('**/*.[Jj][Pp][Gg]', recursive=True)

# Window Layout
leftpane = [
    [sg.Image(key='image')],
]

rightpane = []
line = []
for k, v in headers.items():
    if v['show']:
        line.append(sg.Text(k))
        line.append(sg.InputText(key=k, size=v['size']))
    if v['newline']:
        rightpane.append(line)
        line = []

rightpane.append([sg.Button('prev', key='prev'), sg.Button('next', key='next')])

layout = [
    [sg.Column(leftpane), sg.VSeparator(), sg.Column(rightpane)]
]
window = sg.Window("Edit info", layout, finalize=True, location=(200, 200),
                   keep_on_top=True, enable_close_attempted_event=True)
window.bind("<Alt_L><p>", "altp")
window.bind("<Alt_L><n>", "altn")
window['prev'].Widget.configure(underline=0, takefocus=0)
window['next'].Widget.configure(underline=0, takefocus=0)
bgcolor = window['image'].Widget['background']

# continue from last time commented file
try:
    ix = jpgs.index(lastkey)
except ValueError:
    ix = 0

# one jpg at a time
jpb = ""
while True:
    jpg = jpgs[ix]
    exif = ExImage(jpg)
    timestamp = datetime.strptime(exif.datetime,
                                  "%Y:%m:%d %H:%M:%S").strftime(
                                      "%Y/%m/%d %H:%M:%S").split(' ')[0]
    png = 'temp/' + re.sub('\.[Jj][Pp][Gg]', ".PNG", jpg)
    camnumber = jpg.split('/')[1]
    filename = os.path.basename(jpg)

    # Create PNG in temporaly directory since PySimpleGUI only supports PNG
    # and GIF
    if os.path.exists(png) is False:
        img = Image.open(jpg)
        img.thumbnail((832, 832))

        os.makedirs(os.path.dirname(png), exist_ok=True)
        img.save(png)

    # current info from CSV
    try:
        info = dcsv[jpg]
    except KeyError:
        lk = list(headers.keys())
        info = [''] * len(headers)
        info[lk.index('jpg')] = jpg
        info[lk.index('camnum')] = camnumber
        info[lk.index('filename')] = filename
        info[lk.index('timestamp')] = timestamp

    # show image and info
    window['image'].update(filename=png)
    for i, (k, v) in enumerate(headers.items()):
        if v['show']:
            window[k].update(info[i])

    # notify if there is comments.
    oncmnt = False
    for k, v in headers.items():
        if v['show'] and window[k].get():
            oncmnt = True
            break

    if oncmnt:
        window['image'].ParentRowFrame.config(background='red')
    else:
        window['image'].ParentRowFrame.config(background=bgcolor)

    # wait an event occurs
    event, values = window.read()
    if event in ('prev', 'altp') or event in ('next', 'altn') \
       or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
        debstr = ""
        for i, (k, v) in enumerate(headers.items()):
            if debstr:
                debstr += ", "

            if values and k in values and '' != values[k]:
                info[i] = values[k]
            elif 'jpg' == k:
                info[i] = jpg
            elif 'camnum' == k:
                info[i] = camnumber
            elif 'filename' == k:
                info[i] = filename
            elif 'timestamp' == k:
                info[i] = timestamp
            else:
                info[i] = ''

            debstr += f"{k}={info[i]}"

        print(debstr)
        dcsv[jpg] = info

        if event in ('next', 'altn'):
            ix += 1
            if ix == len(jpgs):
                ix = 0

        if event in ('prev', 'altp'):
            ix -= 1
            if 0 > ix:
                ix = len(jpgs) -1

        if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            break

# bring a last viewing jpg to the end of dict in order to continue from
# the jpg next time.
if jpg:
    dcsv[jpg] = dcsv.pop(jpg)

# write CSV
with open(csvfilename, 'w', encoding='shift_jis', newline='') as f:
    writer = csv.writer(f)
    for key, val in dcsv.items():
        writer.writerow(val)

window.close()
