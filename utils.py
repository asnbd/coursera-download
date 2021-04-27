from time import localtime
from datetime import datetime
from threading import Thread
from pathlib import Path
import os
import re
import requests
from urllib.parse import urlparse
from urllib.parse import urljoin

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


def log(text):
    print("[{}] {}".format(getCurrentTime(), text))


def savePlainFile(path, content):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    file = open(path, "w", encoding='utf-8')
    file.write(content)
    file.close()
    print("Saved to: ", path)

    return os.path.basename(path)


def downloadFile(url, path, filename=None):
    print("Downloading:", url)
    response = requests.get(url)

    if filename is None:
        filename = os.path.basename(urlparse(url).path)

    path = os.path.join(path, filename)
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    file = open(path, "wb")
    file.write(response.content)
    file.close()
    print("Downloaded To:", path)

    return filename


def getFullUrl(base, url):
    if url.startswith("http:") or url.startswith("https:"):
        return url
    else:
        return urljoin(base, url)


def getFile(url):
    print("Downloading:", url)
    response = requests.get(url)

    return response.content



