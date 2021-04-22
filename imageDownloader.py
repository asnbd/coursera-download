import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

root = "I:\Others\Downloads\Coursera\Google Project Management\\03. Project Planning - Putting It All Together"
# path = os.path.join(root, "targetdirectory")

def files():
    error_list = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith(".html"):
                fpath = os.path.join(path, name)
                print(fpath)

                f = open(fpath, "r", encoding='utf-8')
                html_text = f.read()
                f.close()
                soup = BeautifulSoup(html_text, 'html.parser')
                # print(soup.get_text)
                imgTags = soup.find_all('img')
                print(len(imgTags))
                for img in imgTags:
                    imgUrl = img.get('src')
                    if imgUrl.find("../../Resources") >= 0:
                        continue
                    print(imgUrl)
                    try:
                        imgFilename = downloadFile(imgUrl)
                        img['src'] = "../../Resources/html/img/" + imgFilename
                    except Exception as e:
                        print("error")
                        error_list.append(imgUrl)
                        continue
                    # img['src'] = "TEST"
                    print(img)

                if len(imgTags) > 0:
                    saveHtml(fpath, str(soup))
                print()
    print(error_list)

def downloadFile(url):
    response = requests.get(url)
    # print(response.headers)
    filename = os.path.basename(urlparse(url).path)
    print(filename)
    path = os.path.join(root, "Resources", "html", "img", filename)
    print(path)
    file = open(path, "wb")
    file.write(response.content)
    file.close()

    return filename

def saveHtml(path, html):
    print(html)
    file = open(path, "w", encoding='utf-8')
    file.write(html)
    file.close()


if __name__ == '__main__':
    print("main")
    # files()

