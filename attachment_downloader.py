import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
from pathlib import Path
import utils

root = "I:\\Others\\Downloads\\Coursera\\Google Project Management\\Test\\Test1"
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
                attachment_tags = soup.find_all('a', {"class": "cml-asset-link"})
                asset_containers = soup.find_all('div', {"class": "asset-container"})

                print(len(attachment_tags) + len(asset_containers), "attachment(s) found")
                file_modified = False
                total_count += len(attachment_tags) + len(asset_containers)

                new_attachment_href = "../../Resources"

                if fpath.find("{}Resources{}".format(os.path.sep, os.path.sep)) >= 0:
                    new_attachment_href = "../Resources"

                for idx, asset_container in enumerate(asset_containers):
                    attachment_tag = asset_container.find('a')
                    attach_filename = asset_container.find("span", {"class": "asset-name"}).text
                    attach_filename = utils.getFormattedFileName(attach_filename)
                    # print(link.get("href"))
                    attach_href = attachment_tag.get('href')
                    print("Attachment {}/{}:".format(idx + 1, len(asset_containers)), end=" ")
                    if attach_href.find(new_attachment_href) >= 0:
                        print("Already processed. Skipping...")
                        skipped_count += 1
                        continue
                    elif attach_href == "":
                        error_list.append({"error": "blank href", "path": fpath})
                        print("Error: Blank href")
                        continue
                    try:
                        attah_filename = downloadFile(attach_href, attach_filename)
                        file_modified = True
                        processed_count += 1
                        attachment_tag['href'] = new_attachment_href + "/attachments/" + attah_filename
                    except Exception as e:
                        print("Error:", e)
                        error_list.append({"error": "url", "url": attach_href, "path": fpath})
                        continue

                for idx, attachment_tag in enumerate(attachment_tags):
                    attach_href = attachment_tag.get('href')
                    attach_filename = attachment_tag.text
                    attach_filename = utils.getFormattedFileName(attach_filename)
                    print("Attachment {}/{}:".format(idx+1, len(attachment_tags)), end=" ")
                    if attach_href.find(new_attachment_href) >= 0:
                        print("Already processed. Skipping...")
                        skipped_count += 1
                        continue
                    elif attach_href == "":
                        error_list.append({"error": "blank href", "path": fpath})
                        print("Error: Blank href")
                        continue
                    try:
                        attah_filename = downloadFile(attach_href, attach_filename)
                        file_modified = True
                        processed_count += 1
                        attachment_tag['href'] = new_attachment_href + "/attachments/" + attah_filename
                    except Exception as e:
                        print("Error:", e)
                        error_list.append({"error": "url", "url": attach_href, "path": fpath})
                        continue

                if file_modified:
                    saveHtml(fpath, str(soup))
                print()

    print("Total:", total_count, "attachment(s)")
    print("Processed:", processed_count, "attachment(s)")
    print("Skipped:", skipped_count, "attachment(s)")
    print("Errors:", len(error_list))
    print(error_list)

    with open("data/attach_errors.json", "w") as out_file:
        json.dump(error_list, out_file)


def downloadFile(url, filename):
    print("Downloading:", url)
    response = requests.get(url)
    # print(response.headers)
    # filename = os.path.basename(urlparse(url).path)
    # print(filename)
    path = os.path.join(root, "Resources", "attachments", filename)
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

