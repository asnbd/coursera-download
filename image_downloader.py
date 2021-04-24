import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
from pathlib import Path

root = "I:\\Others\\Downloads\\Coursera\\Google Project Management\\06. Capstone"
# path = os.path.join(root, "targetdirectory")

def files():
    error_list = []
    total_count = 0
    skipped_count = 0
    processed_count = 0

    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith(".html"):
                fpath = os.path.join(path, name)
                print("Loading:", fpath)

                f = open(fpath, "r", encoding='utf-8')
                html_text = f.read()
                f.close()
                soup = BeautifulSoup(html_text, 'html.parser')
                # print(soup.get_text)
                imgTags = soup.find_all('img')
                print(len(imgTags), "image(s) found")
                file_modified = False
                total_count += len(imgTags)
                for idx, img in enumerate(imgTags):
                    imgUrl = img.get('src')
                    print("Image {}/{}:".format(idx+1, len(imgTags)), end=" ")
                    if imgUrl.find("../../Resources") >= 0:
                        print("Already processed. Skipping...")
                        skipped_count += 1
                        continue
                    elif imgUrl == "":
                        error_list.append({"error": "blank img src", "path": fpath})
                        print("Error: Blank img src")
                        continue
                    # print(imgUrl)
                    try:
                        imgFilename = downloadFile(imgUrl)
                        file_modified = True
                        processed_count += 1
                        img['src'] = "../../Resources/html/img/" + imgFilename
                    except Exception as e:
                        print("Error:", e)
                        error_list.append({"error": "url", "url": imgUrl ,"path": fpath})
                        continue
                    # img['src'] = "TEST"
                    # print(img)

                if file_modified:
                    saveHtml(fpath, str(soup))
                print()

    print("Total:", total_count, "image(s)")
    print("Processed:", processed_count, "image(s)")
    print("Skipped:", skipped_count, "image(s)")
    print("Errors:", len(error_list))
    print(error_list)

    with open("data/img_errors.json", "w") as out_file:
        json.dump(error_list, out_file)


def downloadFile(url):
    print("Downloading:", url)
    response = requests.get(url)
    # print(response.headers)
    filename = os.path.basename(urlparse(url).path)
    # print(filename)
    path = os.path.join(root, "Resources", "html", "img", filename)
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    print("Downloaded To:", path)
    file = open(path, "wb")
    file.write(response.content)
    file.close()

    return filename

def saveHtml(path, html):
    # print(html)
    file = open(path, "w", encoding='utf-8')
    file.write(html)
    file.close()
    print("Saved: ", path)


if __name__ == '__main__':
    print("main")
    files()

