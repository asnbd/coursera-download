from Bot import Bot
import json
import os
import utils

if __name__ == '__main__':
    # root = os.getcwd()
    root = "I:\\Others\\Downloads\\Coursera\\Google Project Management\\Test"

    homeUrl = "https://www.coursera.org/learn/project-execution-google/home/welcome"

    bot = Bot("main")

    bot.loadUrl(homeUrl)

    # input("Press any key to start...")

    weeks = bot.getWeeks(homeUrl)

    print(weeks)

    data = []

    for week in weeks:
        print(week['title'])
        topics = bot.getTopics(week['url'])
        print(topics)
        print()
        week["topics"] = topics

        data.append(week)
        break

    download_queue = []
    skipped = []

    for week in data:
        topic_index = 1
        for topic in week["topics"]:
            path = os.path.join(week['title'], str(topic_index).zfill(2) + ". " + utils.getFormattedFileName(topic['title']))
            index = 1
            for item in topic["items"]:
                item_type = item['type']
                if item_type == "Video":
                    video_url, captions_url = bot.getVideo(item['url'])
                    filename = str(index).zfill(2) + ". " + item['title']
                    filename = utils.getFormattedFileName(filename)
                    print(path)
                    print(filename)
                    download_queue.append({"path": path, "filename": filename + ".webm", "url": video_url})
                    download_queue.append({"path": path, "filename": filename + ".vtt", "url": captions_url})
                    # print(video)
                    pass

                elif item_type == "Reading":
                    html = bot.getReading(item['title'], item['url'])
                    filename = str(index).zfill(2) + ". Reading - " + item['title']
                    filename = utils.getFormattedFileName(filename) + ".html"
                    print(path)
                    print(filename)
                    print(html)
                    full_path = os.path.join(root, path, filename)
                    print(full_path)
                    utils.saveHtml(full_path, html)
                    pass

                elif item_type == "Quiz":
                    quiz_type, html = bot.getQuiz(item['title'], item['url'])
                    filename = str(index).zfill(2) + ". " + quiz_type + " - " + item['title']
                    filename = utils.getFormattedFileName(filename) + ".html"
                    print(path)
                    print(filename)
                    print(html)
                    full_path = os.path.join(root, path, filename)
                    utils.saveHtml(full_path, html)
                    pass
                elif item_type == "Practice Peer-graded Assignment" or item_type == "Graded Assignment":
                    title, res_html_instructions, res_html_submission = bot.getPeerGradedAssignment(item['url'])
                    filename_instructions = str(index).zfill(2) + ". " + title
                    filename_instructions = utils.getFormattedFileName(filename_instructions) + ".html"

                    filename_submission = str(index).zfill(2) + ". Submission - " + item['title']
                    filename_submission = utils.getFormattedFileName(filename_submission) + ".html"

                    print(path)
                    print(filename_instructions)
                    print(res_html_instructions)

                    print(filename_submission)
                    print(res_html_submission)

                    full_path = os.path.join(root, path, filename_instructions)
                    utils.saveHtml(full_path, res_html_instructions)

                    full_path = os.path.join(root, path, filename_submission)
                    utils.saveHtml(full_path, res_html_submission)
                    pass
                # elif item_type == "Programming Assignment":
                #     pass
                else:
                    skipped.append({"type": item_type, "path": path, "title": item['title'], "url": item['url']})
                    continue

                index += 1

            topic_index += 1

    print(download_queue)

    print("Skipped Items:")
    for item in skipped:
        print(item)

    bot.closeBrowser()

    print(json.dumps(data))
    print("end")


