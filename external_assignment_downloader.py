import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
from pathlib import Path
import utils
from urllib.parse import urljoin
import re


def download(root, links):
    if not links:
        print("Empty Links")
        return False

    error_list = []
    total_count = 0
    skipped_count = 0
    processed_count = 0

    for item in links:
        path = item["path"]
        tmp = path.split("\\")
        prefix = tmp[0].replace("Week ", "0") + tmp[1][:2]

        base_link = item["url"]
        html = getFile(base_link)
        soup = BeautifulSoup(html, 'html.parser')

        # print(soup.get_text)

        title_tag = soup.find('title')
        link_tags = soup.find_all('link')
        script_tags = soup.find_all('script')
        img_tags = soup.find_all('img')

        title = title_tag.text
        folder_name = prefix + "_" + utils.getFormattedFileName(title.lower().replace(" ", "_"))

        # index_file_name = utils.getFormattedFileName(title) + ".html"
        index_file_name = item['filename']

        # print(folder_name)

        print(len(link_tags), "links(s) found")
        print(len(script_tags), "script(s) found")
        print(len(img_tags), "image(s) found")

        # print(link_tags)

        total_count += len(link_tags) + len(script_tags)

        # print(script_tags)

        for idx, link_tag in enumerate(link_tags):
            src = link_tag.get("href")
            url = getFullUrl(base_link, src)
            # print(url)

            print("Link {}/{}:".format(idx + 1, len(link_tags)), end=" ")
            if src == "":
                error_list.append({"error": "blank href", "path": path})
                print("Error: Blank href")
                continue
            try:
                link_filename = downloadFile(url, folder_name)
                processed_count += 1
                link_tag['href'] = "../../Resources/html/" + folder_name + "/" + link_filename
            except Exception as e:
                print("Error:", e)
                error_list.append({"error": "url", "url": url, "path": path})
                continue

        for idx, script_tag in enumerate(script_tags):
            src = script_tag.get("src")
            if src is None:
                print("External src not found. Maybe internal script. Skipping...")
                skipped_count += 1
                continue

            url = getFullUrl(base_link, src)

            print("Script {}/{}:".format(idx + 1, len(link_tags)), end=" ")
            if src == "":
                error_list.append({"error": "blank src", "path": path})
                print("Error: Blank src")
                continue
            try:
                if src.find("main") >= 0:
                    js_file = getFile(url).decode("utf-8")

                    count_static = js_file.count("static")
                    external_links = re.findall("(static[/a-zA-Z._0-9-@]*)", js_file)
                    external_links_count = len(external_links)

                    print("Found {} external links in main.js, now downloading".format(external_links_count))
                    for ext_idx, external_link in enumerate(external_links):
                        external_link_url = urljoin(base_link, external_link)
                        print("External Link {}/{}:".format(ext_idx + 1, external_links_count), end=" ")
                        downloadFile(external_link_url, "media")

                    if count_static != external_links_count:
                        print("WARNING: Downloaded {} external links but found {}".format(external_links_count, count_static))

                    js_file = js_file.replace("static/", "../../Resources/html/")
                    js_file_path = os.path.join(root, "Resources", 'html', folder_name, "main.js")
                    link_filename = saveFile(js_file_path, js_file)
                else:
                    link_filename = downloadFile(url, folder_name)

                processed_count += 1
                script_tag['src'] = "../../Resources/html/" + folder_name + "/" + link_filename
            except Exception as e:
                print("Error:", e)
                error_list.append({"error": "url", "url": url, "path": path})
                continue

        save_path = os.path.join(root, path, index_file_name)
        saveFile(save_path, str(soup))
        print()

    print("Total:", total_count, "file(s)")
    print("Processed:", processed_count, "file(s)")
    print("Skipped:", skipped_count, "file(s)")
    print("Errors:", len(error_list))
    print(error_list)

    # with open("data/attach_errors.json", "w") as out_file:
    #     json.dump(error_list, out_file)

def getFile(url):
    print("Downloading:", url)
    response = requests.get(url)

    return response.content


def downloadFile(url, folder_name, filename=None):
    print("Downloading:", url)
    response = requests.get(url)

    if filename is None:
        filename = os.path.basename(urlparse(url).path)

    path = os.path.join(root, "Resources", 'html', folder_name, filename)
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    file = open(path, "wb")
    file.write(response.content)
    file.close()
    print("Downloaded To:", path)

    return filename


def saveFile(path, content):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)

    file = open(path, "w", encoding='utf-8')
    file.write(content)
    file.close()

    print("Saved: ", path)

    return os.path.basename(path)


def getFullUrl(base, url):
    if url.startswith("http:") or url.startswith("https:"):
        return url
    else:
        return urljoin(base, url)


if __name__ == '__main__':
    print("main")

    root = "I:\\Others\\Downloads\\Coursera\\Google Project Management\\Test\\Test1"

    with open("data/log_20210425_044352/download_queue_assignment.json", "r") as json_file:
        links = json.load(json_file)
        print("Loaded", len(links), "item(s)")

    download(root, links)
