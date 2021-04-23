from driver import Driver
import json
import os
import utils
from pathlib import Path


class Bot:
    def __init__(self, driver: Driver, course_url, output_root, start_week=1, get_video=True, get_reading=True, get_quiz=True, get_graded_assignment=True):
        # self.root = os.getcwd()
        self.root = output_root
        self.home_url = course_url
        self.driver = driver
        self.start_week = start_week

        self.get_video = get_video
        self.get_reading = get_reading
        self.get_quiz = get_quiz
        self.get_graded_assignment = get_graded_assignment

        self.driver.loadUrl(self.home_url)
    
    def run(self):
        # input("Press any key to start...")
    
        weeks = self.driver.getWeeks(self.home_url)

        print(weeks)

        data = []

        for week_idx, week in enumerate(weeks):
            if self.start_week > week_idx + 1:
                print("Skipping Week", week_idx + 1)
                continue
            print(week['title'])
            topics = self.driver.getTopics(week['url'])
            print(topics)
            print()
            week["topics"] = topics

            data.append(week)

        # get_video = False
        # get_reading = False
        # get_quiz = True
        # get_graded_assignment = False

        download_queue = []
        skipped = []
        skipped_important = []

        for week_idx, week in enumerate(data):
            # if start_week > week_idx + 1:
            #     print("Skipping Week", week_idx + 1)
            #     continue

            topic_index = 1
            for topic in week["topics"]:
                path = os.path.join(week['title'], str(topic_index).zfill(2) + ". " + utils.getFormattedFileName(topic['title']))
                index = 1
                for item in topic["items"]:
                    item_type = item['type']
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
                            print(html)
                            full_path = os.path.join(self.root, path, filename)
                            print(full_path)
                            utils.saveHtml(full_path, html)
                        pass

                    elif item_type == "Quiz":
                        if self.get_quiz:
                            quiz_type, html = self.driver.getQuiz(item['title'], item['url'])
                            filename = str(index).zfill(2) + ". " + quiz_type + " - " + item['title']
                            filename = utils.getFormattedFileName(filename) + ".html"
                            print(path)
                            print(filename)
                            print(html)
                            full_path = os.path.join(self.root, path, filename)
                            utils.saveHtml(full_path, html)
                        pass
                    elif item_type == "Practice Peer-graded Assignment" or item_type == "Graded Assignment":
                        if self.get_graded_assignment:
                            title, res_html_instructions, res_html_submission = self.driver.getPeerGradedAssignment(item['url'])
                            filename_instructions = str(index).zfill(2) + ". " + title
                            filename_instructions = utils.getFormattedFileName(filename_instructions) + ".html"

                            filename_submission = str(index).zfill(2) + ". Submission - " + item['title']
                            filename_submission = utils.getFormattedFileName(filename_submission) + ".html"

                            print(path)
                            print(filename_instructions)
                            print(res_html_instructions)

                            print(filename_submission)
                            print(res_html_submission)

                            full_path = os.path.join(self.root, path, filename_instructions)
                            utils.saveHtml(full_path, res_html_instructions)

                            full_path = os.path.join(self.root, path, filename_submission)
                            utils.saveHtml(full_path, res_html_submission)
                        pass
                    elif item_type == "Programming Assignment":
                        skipped_important.append({"type": item_type, "path": path, "title": item['title'], "url": item['url']})
                        pass
                    else:
                        skipped.append({"type": item_type, "path": path, "title": item['title'], "url": item['url']})
                        continue

                    index += 1

                topic_index += 1

        print(download_queue)

        print("Skipped Important Items:")
        for item in skipped_important:
            print(item)

        print("Skipped Items:")
        for item in skipped:
            print(item)

        self.dumpData(data, download_queue, skipped_important, skipped)

        print(json.dumps(data))

    def dumpData(self, data, download_queue, skipped_important, skipped):
        path = "data/" + "log_" + utils.getFormattedDateTimeFile(utils.getCurrentTime().timestamp()) + "/"

        Path(path).mkdir(parents=True, exist_ok=True)

        with open(path + 'data.json', 'w') as outfile:
            json.dump(data, outfile)

        with open(path + 'download_queue.json', 'w') as outfile:
            json.dump(download_queue, outfile)

        with open(path + 'skipped_important.json', 'w') as outfile:
            json.dump(skipped_important, outfile)

        with open(path + 'skipped.json', 'w') as outfile:
            json.dump(skipped, outfile)
