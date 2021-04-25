import json
import requests
import os
from urllib.parse import urlparse
from pathlib import Path
from pySmartDL import SmartDL
import time

if False:
    from gui import App

class FileDownloader:
    current_download_no = 0
    current_download_item = None
    current_download_obj = None
    gui = None

    stop_queue = False

    def __init__(self, root, gui: "App" = None):
        self.download_queue = []
        self.downloading = []
        self.success = []
        self.error = []
        self.download_root = root
        self.gui = gui

    def loadQueueFromJson(self, filename):
        with open(filename, "r") as json_file:
            download_queue = json.load(json_file)
            self.download_queue = download_queue
            print("Loaded", len(download_queue), "item(s)")

    def loadQueueFromList(self, list):
        self.download_queue = list
        print("Loaded", len(list), "item(s)")

    def getDownloadQueueSize(self):
        return len(self.download_queue)

    def startDownload(self, index=0):
        i = 1
        for item in self.download_queue:
            print(i, "of", self.getDownloadQueueSize())
            self.downloadFile(item['url'], item['filename'], item['path'])
            i += 1

    def downloadFile(self, url, filename, path):
        fullpath = os.path.join(self.download_root, path, filename)
        fullpath = os.path.normpath(fullpath)
        Path(os.path.dirname(fullpath)).mkdir(parents=True, exist_ok=True)

        print()
        print("Downloading:", url)
        print("To:", fullpath)

        obj = SmartDL(url, fullpath)
        obj.start()

        return filename

    def startDownloadGui(self, index=0):
        i = 1
        for item in self.download_queue:
            self.current_download_no = i
            self.current_download_item = item
            print(i, "of", self.getDownloadQueueSize())
            self.downloadFileGui(item['url'], item['filename'], item['path'])
            i += 1
            if self.stop_queue:
                self.stop_queue = False
                return

        self.gui.showDownloadCompleteDialog()

    def downloadFileGui(self, url, filename, path):
        fullpath = os.path.join(self.download_root, path, filename)
        fullpath = os.path.normpath(fullpath)
        Path(os.path.dirname(fullpath)).mkdir(parents=True, exist_ok=True)

        print()
        print("Downloading:", url)
        print("To:", fullpath)

        self.current_download_obj = SmartDL(url, fullpath, progress_bar=False)
        self.current_download_obj.start(blocking=False)

        while not self.current_download_obj.isFinished():
            download_info = self.getDownloadInfo(fullpath)

            if self.stop_queue:
                self.stop()
                return

            if download_info:
                self.gui.setVideoDownloadProgress(download_info)
            time.sleep(0.1)

        return filename

    def getDownloadInfo(self, full_path):
        download_info = None

        try:
            if self.current_download_obj is not None:
                # print(self.current_download_obj)
                download_info = {"total_files": self.getDownloadQueueSize(),
                                 "current_no": self.current_download_no,
                                 "item": self.current_download_item,
                                 "full_path": full_path,
                                 "speed": self.current_download_obj.get_speed(human=True),
                                 "dl_size": self.current_download_obj.get_dl_size(human=True),
                                 "total_size": self.current_download_obj.get_final_filesize(human=True),
                                 "eta": self.current_download_obj.get_eta(human=True),
                                 "progress": self.current_download_obj.get_progress() * 100,
                                 "progress_bar": self.current_download_obj.get_progress_bar(),
                                 "status": self.current_download_obj.get_status()}
        except Exception as e:
            print("Error:", e)

        return download_info

    def pause(self):
        if self.current_download_obj is not None:
            self.current_download_obj.pause()
            return True

        return False

    def resume(self):
        if self.current_download_obj is not None and self.current_download_obj.status == "paused":
            self.current_download_obj.resume()
            return True

        return False

    def stop(self):
        if self.current_download_obj is not None:
            self.current_download_obj.stop()
            return True

        return False

    def stopQueue(self):
        if self.current_download_obj is not None:
            self.stop_queue = True
            self.current_download_obj.stop()
            return True

        return False

    def attachGUI(self, gui: "App"):
        self.gui = gui

    def isGuiAttached(self):
        return True if self.gui is not None else False


if __name__ == "__main__":
    root = "I:\\Others\\Downloads\\Coursera\\Google Project Management\\Test"
    downloader = FileDownloader(root)

    downloader.loadQueueFromJson("data/log_20210424_031453/download_queue.json")
    downloader.startDownload()
