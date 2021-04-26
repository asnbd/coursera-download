import os
from bs4 import BeautifulSoup
import json
import utils

if False:
    from gui import App


def download(root, gui: "App" = None):
    error_list = []
    total_count = 0
    skipped_count = 0
    processed_count = 0

    attachments_path = os.path.join(root, "Resources", "attachments")

    html_file_count = 0
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith(".html"):
                html_file_count += 1

    current_file_idx = 0
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith(".html"):
                current_file_idx += 1
                fpath = os.path.join(path, name)
                print("Loading:", fpath)

                setGuiFileDownloaderInfo(gui, week="Searching", topic="All html files", filename="", url="", output="",
                                         eta="", speed="", dl_size="", file_size="", progress=0, current_no=0,
                                         total_files=0)

                f = open(fpath, "r", encoding='utf-8')
                html_text = f.read()
                f.close()
                soup = BeautifulSoup(html_text, 'html.parser')
                # print(soup.get_text)
                attachment_tags = soup.find_all('a', {"class": "cml-asset-link"})
                asset_containers = soup.find_all('div', {"class": "asset-container"})

                print(len(attachment_tags) + len(asset_containers), "attachment(s) found")
                file_modified = False

                current_file_total_count = len(attachment_tags) + len(asset_containers)
                total_count += current_file_total_count

                new_attachment_href = "../../Resources"

                if fpath.find("{}Resources{}".format(os.path.sep, os.path.sep)) >= 0:
                    new_attachment_href = "../Resources"

                if len(asset_containers) == 0:
                    # Update GUI Progress
                    dl_size = "{} of {}".format(0, 0)
                    setGuiFileDownloaderInfo(gui, week="Loading", topic="", filename=name, url="", output=fpath,
                                             dl_size=dl_size, file_size="", progress=100, current_no=current_file_idx,
                                             total_files=html_file_count)

                for idx, asset_container in enumerate(asset_containers):
                    attachment_tag = asset_container.find('a')
                    attach_filename = asset_container.find("span", {"class": "asset-name"}).text
                    attach_filename = utils.getFormattedFileName(attach_filename)
                    # print(link.get("href"))
                    attach_href = attachment_tag.get('href')

                    # Update GUI Progress
                    progress = (idx + 1) / current_file_total_count * 100
                    dl_size = "{} of {}".format(idx + 1, current_file_total_count)
                    setGuiFileDownloaderInfo(gui, week="Loading", topic="", filename=name, url=attach_href,
                                             output=fpath, dl_size=dl_size, file_size="", progress=progress,
                                             current_no=current_file_idx, total_files=html_file_count)

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
                        attah_filename = utils.downloadFile(attach_href, attachments_path, attach_filename)
                        file_modified = True
                        processed_count += 1
                        attachment_tag['href'] = new_attachment_href + "/attachments/" + attah_filename
                    except Exception as e:
                        print("Error:", e)
                        error_list.append({"error": "url", "url": attach_href, "path": fpath})
                        continue

                if len(attachment_tags) == 0:
                    # Update GUI Progress
                    dl_size = "{} of {}".format(0, 0)
                    setGuiFileDownloaderInfo(gui, week="Loading", topic="", filename=name, url="", output=fpath,
                                             dl_size=dl_size, file_size="", progress=100, current_no=current_file_idx,
                                             total_files=html_file_count)

                for idx, attachment_tag in enumerate(attachment_tags):
                    attach_href = attachment_tag.get('href')
                    attach_filename = attachment_tag.text
                    attach_filename = utils.getFormattedFileName(attach_filename)

                    # Update GUI Progress
                    progress = (len(asset_containers) + idx + 1) / current_file_total_count * 100
                    dl_size = "{} of {}".format(len(asset_containers) + idx + 1, current_file_total_count)
                    setGuiFileDownloaderInfo(gui, week="Loading", topic="", filename=name, url=attach_href,
                                             output=fpath, dl_size=dl_size, file_size="", progress=progress,
                                             current_no=current_file_idx, total_files=html_file_count)

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
                        attah_filename = utils.downloadFile(attach_href, attachments_path, attach_filename)
                        file_modified = True
                        processed_count += 1
                        attachment_tag['href'] = new_attachment_href + "/attachments/" + attah_filename
                    except Exception as e:
                        print("Error:", e)
                        error_list.append({"error": "url", "url": attach_href, "path": fpath})
                        continue

                if file_modified:
                    utils.savePlainFile(fpath, str(soup))
                print()

    print("Total:", total_count, "attachment(s)")
    print("Processed:", processed_count, "attachment(s)")
    print("Skipped:", skipped_count, "attachment(s)")
    print("Errors:", len(error_list))
    print(error_list)

    # setGuiFileDownloaderInfo(gui, week="Success", topic="Attachment processing finished successfully!")

    with open("data/attach_errors.json", "w") as out_file:
        json.dump(error_list, out_file)

# GUI Functions
def setGuiFileDownloaderInfo(gui, week=None, topic=None, filename=None, url=None, output=None, eta=None,
                             speed=None, dl_size=None, file_size=None, progress=None, current_no=0, total_files=0):
    if gui is not None:
        gui.setFileDownloaderInfo(week=week, topic=topic, filename=filename, url=url, output=output, eta=eta,
                                  speed=speed, dl_size=dl_size, file_size=file_size, progress=progress,
                                  current_no=current_no, total_files=total_files)
