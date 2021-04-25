from driver import Driver
import json
import os
import utils
from pathlib import Path
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin


if False:
    from gui import App

class Bot:
    meta_data = []
    download_queue = []
    download_queue_assignment = []
    skipped = []
    skipped_important = []

    gui: "App" = None

    def __init__(self, driver: Driver, course_url=None, output_root=None, start_week=1, get_video=True, get_reading=True,
                 get_quiz=True, get_graded_assignment=True, get_external_exercise=True, gui=None):
        # self.root = os.getcwd()
        self.root = output_root
        self.home_url = course_url
        self.driver = driver
        self.start_week = start_week

        self.get_video = get_video
        self.get_reading = get_reading
        self.get_quiz = get_quiz
        self.get_graded_assignment = get_graded_assignment
        self.get_external_exercise = get_external_exercise

        self.gui = gui

        # self.driver.loadUrl(self.home_url)

    def setCourseUrl(self, url):
        self.home_url = url

    def setDownloadTopics(self, topics):
        self.get_video, self.get_reading, self.get_quiz, self.get_graded_assignment, self.get_external_exercise = topics

    def setOutputRoot(self, output_root):
        self.root = output_root
    
    def run(self):
        # input("Press any key to start...")

        data = self.loadMeta()
        self.downloadHtmlAndGetVideoQueue(data)

    def loadMeta(self):
        if self.isGuiAttached():
            self.gui.setFileDownloaderInfo(week="", topic="Loading Weeks...")

        if not self.home_url:
            return False

        weeks = self.driver.getWeeks(self.home_url)

        print(weeks)

        data = []

        total_weeks = len(weeks)

        if self.isGuiAttached():
            self.gui.setFileDownloaderInfo(week="", topic="Loading Metadata...")

        for week_idx, week in enumerate(weeks):
            # if self.isGuiAttached():
            #     self.gui.setFileDownloaderInfo(week=week['title'], progress=1, current_no=week_idx+1, total_files=total_weeks)

            if self.isGuiAttached():
                self.gui.setFileDownloaderInfo(week=week['title'], progress=0, current_no=week_idx+1, total_files=total_weeks)

            if self.start_week > week_idx + 1:
                print("Skipping Week", week_idx + 1)
                continue

            print(week['title'])
            topics = self.driver.getTopics(week['url'])
            print(topics)
            print()
            week["topics"] = topics

            data.append(week)

        self.meta_data = data

        if self.isGuiAttached():
            self.gui.setFileDownloaderInfo(topic="Metadata Loaded!", progress=100, current_no=total_weeks, total_files=total_weeks)

        return data

    def downloadResources(self):
        if self.isGuiAttached():
            self.gui.setFileDownloaderInfo(week="Fetching", topic="Resources")

        respurce_url = self.home_url.replace("home/welcome", "resources")
        resource_items = self.driver.getResourceLinks(respurce_url)

        print(resource_items)
        resource_path = "Resources"

        total_items = len(resource_items)

        for res_idx, item in enumerate(resource_items):
            filename = str(res_idx + 1).zfill(2) + ". " + item['title']
            filename = utils.getFormattedFileName(filename) + ".html"
            full_path = os.path.join(self.root, resource_path, filename)

            if self.isGuiAttached():
                self.gui.setFileDownloaderInfo(week="Loading", topic="Resources", filename=item['title'], url=item['url'],
                                               output=full_path, progress=0, current_no=res_idx+1, total_files=total_items)
            item_type = item['type']

            # if item_type == "Reading":

            html = self.driver.getResource(item['title'], item['url'])
            print("Resource {}/{}:".format(res_idx + 1, len(resource_items)), end=" ")
            print(filename)
            # print(html)

            # print(full_path)
            utils.savePlainFile(full_path, html)

            print()

        if self.isGuiAttached():
            self.gui.setFileDownloaderInfo(week="Done", topic="Resource Downloaded!",
                                           progress=100, current_no=total_items, total_files=total_items)

        print("Resource Download Finished")

        return True

    def downloadHtmlAndGetVideoQueue(self, data):
        download_queue = []
        download_queue_assignment = []
        skipped = []
        skipped_important = []

        item_count = [0 for i in data]

        for w_idx, week in enumerate(data):
            for topic in week['topics']:
                item_count[w_idx] += len(topic['items'])

        current_total_item_no = 0
        for week_idx, week in enumerate(data):
            # if start_week > week_idx + 1:
            #     print("Skipping Week", week_idx + 1)
            #     continue

            topic_index = 1
            current_week_item_no = 0
            for topic in week["topics"]:
                path = os.path.join(week['title'],
                                    str(topic_index).zfill(2) + ". " + utils.getFormattedFileName(topic['title']))
                index = 1
                for item in topic["items"]:
                    current_week_item_no += 1
                    current_total_item_no += 1

                    item_type = item['type']

                    if self.isGuiAttached():
                        dl_topic = "{}. {}".format(str(topic_index).zfill(2), topic['title'])
                        dl_title = "{}. {}: {}".format(str(index).zfill(2), item_type, item['title'])

                        progress = current_week_item_no / item_count[week_idx] * 100
                        dl_size = "{} of {} item(s)".format(current_week_item_no, item_count[week_idx])
                        self.gui.setFileDownloaderInfo(week=week['title'], topic=dl_topic, progress=progress,
                                                       filename=dl_title,  dl_size=dl_size, url=item['url'],
                                                       output=path, current_no=current_total_item_no, total_files=sum(item_count))

                    if item_type == "Video":
                        if self.get_video:
                            video_url, captions_url = self.driver.getVideo(item['url'])
                            filename = str(index).zfill(2) + ". " + item['title']
                            filename = utils.getFormattedFileName(filename)
                            print(path)
                            print(filename)
                            download_queue.append({"path": path, "filename": filename + ".webm", "url": video_url})
                            download_queue.append({"path": path, "filename": filename + ".vtt", "url": captions_url})
                            # print(video)
                        pass

                    elif item_type == "Reading":
                        if self.get_reading:
                            html = self.driver.getReading(item['title'], item['url'])
                            filename = str(index).zfill(2) + ". Reading - " + item['title']
                            filename = utils.getFormattedFileName(filename) + ".html"
                            print(path)
                            print(filename)
                            # print(html)
                            full_path = os.path.join(self.root, path, filename)
                            # print(full_path)
                            utils.savePlainFile(full_path, html)
                        pass

                    elif item_type == "Quiz":
                        if self.get_quiz:
                            quiz_type, html = self.driver.getQuiz(item['title'], item['url'])
                            filename = str(index).zfill(2) + ". " + quiz_type + " - " + item['title']
                            filename = utils.getFormattedFileName(filename) + ".html"
                            print(path)
                            print(filename)
                            # print(html)
                            full_path = os.path.join(self.root, path, filename)
                            utils.savePlainFile(full_path, html)
                        pass
                    elif item_type == "Practice Peer-graded Assignment" or item_type == "Graded Assignment":
                        if self.get_graded_assignment:
                            title, res_html_instructions, res_html_submission = self.driver.getPeerGradedAssignment(
                                item['url'])
                            filename_instructions = str(index).zfill(2) + ". " + title
                            filename_instructions = utils.getFormattedFileName(filename_instructions) + ".html"

                            filename_submission = str(index).zfill(2) + ". Submission - " + item['title']
                            filename_submission = utils.getFormattedFileName(filename_submission) + ".html"

                            print(path)
                            print(filename_instructions)
                            # print(res_html_instructions)

                            print(filename_submission)
                            # print(res_html_submission)

                            full_path = os.path.join(self.root, path, filename_instructions)
                            utils.savePlainFile(full_path, res_html_instructions)

                            full_path = os.path.join(self.root, path, filename_submission)
                            utils.savePlainFile(full_path, res_html_submission)
                        pass
                    elif item_type == "Programming Assignment":
                        if self.get_external_exercise:
                            assignment_url = self.driver.getAssignmentFrame(item['url'])
                            filename = str(index).zfill(2) + ". " + item['title']
                            filename = utils.getFormattedFileName(filename) + ".html"
                            print(path)
                            print(filename)
                            download_queue_assignment.append({"path": path, "filename": filename, "url": assignment_url, "ref": item['url']})
                            skipped_important.append(
                                {"type": item_type, "path": path, "title": item['title'], "url": item['url']})
                    else:
                        skipped.append({"type": item_type, "path": path, "title": item['title'], "url": item['url']})
                        continue

                    index += 1
                    print()

                topic_index += 1
                print()
            print()

        self.download_queue = download_queue
        self.download_queue_assignment = download_queue_assignment
        self.skipped_important = skipped_important
        self.skipped = skipped

        print(download_queue)

        print("Skipped Important Items:")
        for item in skipped_important:
            print(item)

        print("Skipped Items:")
        for item in skipped:
            print(item)

        self.dumpData(data, download_queue, download_queue_assignment, skipped_important, skipped)

        print(json.dumps(data))

        return download_queue, download_queue_assignment

    def downloadExternalExercise(self):
        root = self.root
        links = self.download_queue_assignment

        if not links:
            print("Empty Links")
            return False

        error_list = []
        total_count = 0
        skipped_count = 0
        processed_count = 0

        self.setGuiFileDownloaderInfo(week="Loading", topic="External Exercise", filename="", url="", output="", eta="",
                                      speed="", dl_size="", file_size="", progress=0, current_no=0, total_files=0)

        total_links = len(links)

        for link_idx, item in enumerate(links):
            path = item["path"]
            tmp = path.split("\\")
            week = tmp[0]
            topic = tmp[1]
            prefix = week.replace("Week ", "0") + topic[:2]

            base_link = item["url"]
            html = utils.getFile(base_link)
            soup = BeautifulSoup(html, 'html.parser')

            # print(soup.get_text)

            title_tag = soup.find('title')
            link_tags = soup.find_all('link')
            script_tags = soup.find_all('script')
            img_tags = soup.find_all('img')

            title = title_tag.text
            folder_name = prefix + "_" + utils.getFormattedFileName(title.lower().replace(" ", "_"))

            resource_path = os.path.join(root, "Resources", 'html', folder_name)
            media_path = os.path.join(root, "Resources", 'html', "media")

            # index_file_name = utils.getFormattedFileName(title) + ".html"
            index_file_name = item['filename']

            # print(folder_name)

            print(len(link_tags), "links(s) found")
            print(len(script_tags), "script(s) found")
            print(len(img_tags), "image(s) found")

            # print(link_tags)

            link_total_count = len(link_tags) + len(script_tags)
            total_count += link_total_count

            # print(script_tags)

            for idx, link_tag in enumerate(link_tags):
                src = link_tag.get("href")
                url = utils.getFullUrl(base_link, src)
                # print(url)

                # Update GUI Progress
                progress = (idx + 1) / link_total_count * 100
                dl_size = "{} of {}".format(idx + 1, link_total_count)
                self.setGuiFileDownloaderInfo(week=week, topic=topic, filename=index_file_name, url=url,
                                              output=resource_path, dl_size=dl_size, file_size="", progress=progress,
                                              current_no=link_idx + 1, total_files=total_links)

                print("Link {}/{}:".format(idx + 1, len(link_tags)), end=" ")
                if src == "":
                    error_list.append({"error": "blank href", "path": path})
                    print("Error: Blank href")
                    continue
                try:
                    link_filename = utils.downloadFile(url, resource_path)
                    processed_count += 1
                    link_tag['href'] = "../../Resources/html/" + folder_name + "/" + link_filename
                except Exception as e:
                    print("Error:", e)
                    error_list.append({"error": "url", "url": url, "path": path})
                    continue

            for idx, script_tag in enumerate(script_tags):
                progress = (len(link_tags) + idx + 1) / link_total_count * 100
                dl_size = "{} of {}".format(len(link_tags) + idx + 1, link_total_count)

                # Update GUI Progress
                self.setGuiFileDownloaderInfo(week=week, topic=topic, filename=index_file_name,
                                              output=resource_path, dl_size=dl_size, file_size="",
                                              progress=progress, current_no=link_idx + 1, total_files=total_links)

                src = script_tag.get("src")
                if src is None:
                    print("External src not found. Maybe internal script. Skipping...")
                    skipped_count += 1
                    continue

                url = utils.getFullUrl(base_link, src)

                # Update GUI Progress
                self.setGuiFileDownloaderInfo(week=week, topic=topic, filename=index_file_name, url=url,
                                              output=resource_path, dl_size=dl_size, file_size="", progress=progress,
                                              current_no=link_idx + 1, total_files=total_links)

                print("Script {}/{}:".format(idx + 1, len(link_tags)), end=" ")
                if src == "":
                    error_list.append({"error": "blank src", "path": path})
                    print("Error: Blank src")
                    continue
                try:
                    if src.find("main") >= 0:
                        js_file = utils.getFile(url).decode("utf-8")

                        count_static = js_file.count("static")
                        external_links = re.findall("(static[/a-zA-Z._0-9-@]*)", js_file)
                        external_links_count = len(external_links)

                        print("Found {} external links in main.js, now downloading".format(external_links_count))
                        for ext_idx, external_link in enumerate(external_links):
                            external_link_url = urljoin(base_link, external_link)

                            # Update GUI Progress
                            curr_progress = (ext_idx + 1) / len(external_links)
                            prev_progress = (len(link_tags) + idx) / link_total_count * 100
                            progress = prev_progress + (100 * curr_progress / link_total_count)
                            # progress = (len(link_tags) + idx + 1 + ext_idx + 1) / (link_total_count + len(external_links)) * 100
                            # dl_size = "{} of {}".format(len(link_tags) + idx + 1 + ext_idx + 1, link_total_count + len(external_links))
                            dl_size = "{} of {}".format(len(link_tags) + idx + 1, link_total_count)
                            self.setGuiFileDownloaderInfo(week=week, topic=topic, filename=index_file_name,
                                                          url=external_link_url, output=resource_path, dl_size=dl_size,
                                                          file_size="", progress=progress, current_no=link_idx + 1,
                                                          total_files=total_links)

                            print("External Link {}/{}:".format(ext_idx + 1, external_links_count), end=" ")
                            utils.downloadFile(external_link_url, media_path)

                        if count_static != external_links_count:
                            print("WARNING: Downloaded {} external links but found {}".format(external_links_count,
                                                                                              count_static))

                        js_file = js_file.replace("static/", "../../Resources/html/")
                        js_file_path = os.path.join(root, "Resources", 'html', folder_name, "main.js")
                        link_filename = utils.savePlainFile(js_file_path, js_file)
                    else:
                        link_filename = utils.downloadFile(url, resource_path)

                    processed_count += 1
                    script_tag['src'] = "../../Resources/html/" + folder_name + "/" + link_filename
                except Exception as e:
                    print("Error:", e)
                    error_list.append({"error": "url", "url": url, "path": path})
                    continue

            save_path = os.path.join(root, path, index_file_name)
            utils.savePlainFile(save_path, str(soup))
            print()

        print("Total:", total_count, "file(s)")
        print("Processed:", processed_count, "file(s)")
        print("Skipped:", skipped_count, "file(s)")
        print("Errors:", len(error_list))
        print(error_list)

    def dumpData(self, data, download_queue, download_queue_assignment, skipped_important, skipped):
        path = "data/" + "log_" + utils.getFormattedDateTimeFile(utils.getCurrentTime().timestamp()) + "/"

        Path(path).mkdir(parents=True, exist_ok=True)

        with open(path + 'data.json', 'w') as outfile:
            json.dump(data, outfile)

        with open(path + 'download_queue.json', 'w') as outfile:
            json.dump(download_queue, outfile)

        with open(path + 'download_queue_assignment.json', 'w') as outfile:
            json.dump(download_queue_assignment, outfile)

        with open(path + 'skipped_important.json', 'w') as outfile:
            json.dump(skipped_important, outfile)

        with open(path + 'skipped.json', 'w') as outfile:
            json.dump(skipped, outfile)

    def attachGUI(self, gui: "App"):
        self.gui = gui

    def isGuiAttached(self):
        return True if self.gui is not None else False

    def setGuiFileDownloaderInfo(self, week=None, topic=None, filename=None, url=None, output=None, eta=None,
                                 speed=None, dl_size=None, file_size=None, progress=None, current_no=0, total_files=0):
        if self.isGuiAttached():
            self.gui.setFileDownloaderInfo(week=week, topic=topic, filename=filename, url=url, output=output, eta=eta,
                                           speed=speed, dl_size=dl_size, file_size=file_size, progress=progress,
                                           current_no=current_no, total_files=total_files)
