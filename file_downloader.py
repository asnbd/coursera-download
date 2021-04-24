import json
import requests
import os
from urllib.parse import urlparse
# from homura import download
from pathlib import Path
from pySmartDL import SmartDL
import time

class FileDownloader:
    current_download_no = 0
    current_download_item = None
    current_download_obj = None
    gui = None

    def __init__(self, root):
        self.download_queue = []
        self.downloading = []
        self.success = []
        self.error = []
        self.download_root = root
        pass

    def loadQueueFromJson(self, filename):
        with open(filename, "r") as json_file:
            download_queue = json.load(json_file)
            self.download_queue = download_queue
            print("Loaded", len(download_queue), "item(s)")

    def getDownloadQueueSize(self):
        return len(self.download_queue)

    def startDownload(self, index=0):
        i = 1
        for item in self.download_queue:
            print(i, "of", self.getDownloadQueueSize())
            self.downloadFile(item['url'], item['filename'], item['path'])
            i += 1

    def downloadFile(self, url, filename, path):
        # response = requests.get(url)
        # # print(response.headers)
        # # filename = os.path.basename(urlparse(url).path)
        # # print(filename)
        fullpath = os.path.join(self.download_root, path, filename)
        Path(os.path.dirname(fullpath)).mkdir(parents=True, exist_ok=True)
        # print(path)
        # file = open(path, "wb")
        # file.write(response.content)
        # file.close()

        print()
        print("Downloading:", url)
        print("To:", fullpath)

        # download(url=url, path=fullpath)

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

    def downloadFileGui(self, url, filename, path):
        fullpath = os.path.join(self.download_root, path, filename)
        Path(os.path.dirname(fullpath)).mkdir(parents=True, exist_ok=True)

        print()
        print("Downloading:", url)
        print("To:", fullpath)

        self.current_download_obj = SmartDL(url, fullpath, progress_bar=False)
        self.current_download_obj.start(blocking=False)

        while not self.current_download_obj.isFinished():
            download_info = self.getDownloadInfo(fullpath)

            if download_info:
                self.gui.setVideoDownloadProgress(download_info)
            time.sleep(0.1)

        return filename

    def getDownloadInfo(self, full_path):
        download_info = None
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

        return download_info

    def attachGUI(self, gui):
        self.gui = gui


if __name__ == "__main__":
    root = "I:\\Others\\Downloads\\Coursera\\Google Project Management\\Test"
    downloader = FileDownloader(root)

    downloader.loadQueueFromJson("data/log_20210424_031453/download_queue.json")
    downloader.startDownload()
    #
    # download(url='http://download.thinkbroadband.com/200MB.zip',
    #          path='/big.zip')