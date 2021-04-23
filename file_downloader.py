import json
import requests
import os
from urllib.parse import urlparse
# from homura import download
from pathlib import Path
from pySmartDL import SmartDL


class FileDownloader:
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
        fullpath = os.path.join(root, path, filename)
        Path(os.path.dirname(fullpath)).mkdir(parents=True, exist_ok=True)
        # print(path)
        # file = open(path, "wb")
        # file.write(response.content)
        # file.close()

        print("Downloading:", url)
        print("To:", fullpath)

        # download(url=url, path=fullpath)

        obj = SmartDL(url, fullpath)
        obj.start()

        return filename

if __name__ == "__main__":
    root = "I:\\Others\\Downloads\\Coursera\\Google Project Management\\Test"
    downloader = FileDownloader(root)

    downloader.loadQueueFromJson("data/download_queue.json")
    downloader.startDownload()
    #
    # download(url='http://download.thinkbroadband.com/200MB.zip',
    #          path='/big.zip')