from time import localtime
from datetime import datetime
from threading import Thread
import winsound
from pathlib import Path
import os
import re

def formatTime(time_in_sec):
    r_time_in_sec = round(time_in_sec)
    hours = r_time_in_sec // 3600
    minutes = r_time_in_sec // 60 % 60
    seconds = r_time_in_sec % 60
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)


def getFormattedTime(time_in_sec):
    time_struct = localtime(time_in_sec)
    hours = time_struct.tm_hour
    minutes = time_struct.tm_min
    seconds = time_struct.tm_sec
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)


def getCurrentTime():
    return datetime.now()


def getFormattedDateTimeFile(time_in_sec):
    time_struct = localtime(time_in_sec)

    year = time_struct.tm_year
    month = time_struct.tm_mon
    day = time_struct.tm_mday

    hours = time_struct.tm_hour
    minutes = time_struct.tm_min
    seconds = time_struct.tm_sec

    return "{:02d}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(year, month, day, hours, minutes, seconds)


def getFormattedFileName(filename):
    filename = filename.replace("/", " ")
    filename = filename.replace("?", "")
    filename = filename.replace(":", "-")
    filename = filename.replace('"', "'")
    filename = filename.replace('\r\n', " ")
    filename = filename.replace('\n', " ")
    filename = re.sub(' +', ' ', filename)
    return filename

def playBeep():
    Thread(target=runPlayBeepThread).start()


def playShortBeep():
    Thread(target=runPlayBeepThread, args=(1500, 90)).start()


def runPlayBeepThread(frequency=2000, duration=200):
    winsound.Beep(frequency, duration)


def log(text):
    print("[{}] {}".format(getCurrentTime(), text))


def saveHtml(path, html):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    file = open(path, "w", encoding='utf-8')
    file.write(html)
    file.close()
    print("Saved to: ", path)

