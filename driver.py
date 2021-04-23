from selenium import webdriver
import os
import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class Driver:
    def __init__(self, name):
        self.profile_name = name
        profile_dir = os.path.join(os.getcwd(), "profiles", self.profile_name)

        chrome_options = webdriver.ChromeOptions()

        chrome_options.set_capability("pageLoadStrategy", "none")
        chrome_options.set_capability("webdriver.load.strategy", "none")
        chrome_options.add_argument("user-data-dir=" + profile_dir)

        self.driver = webdriver.Chrome(executable_path="chromedriver_win32/chromedriver.exe", options=chrome_options)  # , desired_capabilities=capabilities

    ###################################################################################################################
    """" Action Functions """
    ###################################################################################################################
    def back(self):
        # TODO implement browser back
        pass

    def getWeeks(self, url):
        self.loadUrl(url)
        try:
            element = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".week-number"))
            )
        except Exception as e:
            utils.log(e)

        weeks = self.driver.find_elements_by_xpath("//a[contains(@class,'rc-WeekNavigationItem')]")

        result = []

        for week in weeks:
            week_title = week.get_attribute("innerText")
            week_url = week.get_attribute("href")
            # print(week_title)
            # print(week_url)
            result.append({"title": week_title, "url": week_url})

        return result

    def getTopics(self, url):
        self.loadUrl(url)
        # self.driver.refresh()
        try:
            element = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".rc-WeekItemName")),
            )
        except Exception as e:
            utils.log(e)

        time.sleep(3)

        lessons = self.driver.find_elements_by_xpath("//div[contains(@class,'rc-NamedItemList')]")
        result = []

        for lesson in lessons:
            lesson_title = lesson.find_element_by_xpath("div[contains(@class,'named-item-list-title')]").text
            lesson_items = lesson.find_elements_by_xpath("ul//li//a")
            # print(lesson_title)

            lesson_items_list = []

            for lesson_item in lesson_items:
                lesson_item_url = lesson_item.get_attribute('href')
                title = lesson_item.find_element_by_class_name('rc-WeekItemName')
                lesson_item_title = self.driver.execute_script('return arguments[0].lastChild.textContent;', title).strip()
                # print(lesson_item_title)

                lesson_item_type = lesson_item.find_element_by_tag_name("title").get_attribute('innerHTML')

                if lesson_item_type == "Review Your Peers":
                    peer_header = title.find_element_by_tag_name("strong").text
                    if peer_header.find("Practice") >= 0:
                        lesson_item_type = "Practice Peer-graded Assignment"
                        # print(lesson_item_type)

                # print(lesson_item_type)

                lesson_items_list.append({"title": lesson_item_title, "type": lesson_item_type, "url": lesson_item_url})
                # print(lesson_item_url)
                # print()

            # print()

            result.append({"title": lesson_title, "items": lesson_items_list})

            self.driver.implicitly_wait(3)

        return result

    def getVideo(self, url):
        self.loadUrl(url)
        try:
            element = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".video-main-player-container")),
            )
        except Exception as e:
            utils.log(e)

        time.sleep(3)

        captions = self.driver.find_element_by_xpath("//video//track[@kind='captions']")
        captions_url = captions.get_attribute('src')

        # increase_video_size_btn = self.driver.execute_script("document.getElementsByClassName('resolution-change-controls')[0].firstChild")

        # print(self.driver.execute_script("document.getElementsByClassName('resolution-change-controls')[0].lastChild.disabled"))
        # increase_video_size_btn.click()

        for retry in range(10):
            video = self.driver.find_element_by_xpath("//video")
            video_url = video.get_attribute('src')

            if video_url.find("720p") < 0:
                print("video is not 720p. Recapturing...")
                # input("Press any key to recapture...")
                self.driver.execute_script(
                    "document.getElementsByClassName('resolution-change-controls')[0].lastChild.click()")
                self.driver.execute_script(
                    "document.getElementsByClassName('resolution-change-controls')[0].lastChild.click()")
                time.sleep(1)
                # increase_video_size_btn.click()
                # increase_video_size_btn.click()
            else:
                break

        return video_url, captions_url

    def getReading(self, title, url):
        self.loadUrl(url)
        try:
            element = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".reading-header")),
            )
        except Exception as e:
            utils.log(e)

        time.sleep(3)

        html_body = self.driver.find_element_by_id("main").get_attribute('outerHTML')

        res_html = "<!DOCTYPE html>\n<html lang=\"en\">\n <head>\n   <title>" + title + '</title>\n   <link rel="stylesheet" href="../../Resources/html/styles.css" />\n </head>\n<body>' + html_body + "\n</body>\n</html>"

        return res_html

    def getQuiz(self, title, url):
        self.loadUrl(url)
        try:
            element = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "._1f8f5kai")),
            )
        except Exception as e:
            utils.log(e)

        # time.sleep(3)

        resume_button = self.driver.find_element_by_class_name("_1f8f5kai")
        resume_button.click()

        try:
            element = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".rc-FormPartsQuestion")),
            )
        except Exception as e:
            utils.log(e)

        time.sleep(3)

        # header = self.driver.find_element_by_class_name("_125g251l").get_attribute('innerHTML')
        quiz_type = self.driver.find_element_by_class_name("rc-HeaderLeft__sub-header")
        quiz_type = self.driver.execute_script('return arguments[0].firstChild.textContent;', quiz_type).strip()

        html_body = self.driver.find_element_by_class_name("rc-TunnelVisionWrapper__content-body").get_attribute('outerHTML')

        res_html = "<!DOCTYPE html>\n<html lang=\"en\">\n <head>\n   <title>" + title + '</title>\n   <link rel="stylesheet" href="../../Resources/html/styles.css" />\n </head>\n<body>' + html_body + "\n</body>\n</html>"

        return quiz_type, res_html

    def getPeerGradedAssignment(self, url):
        self.loadUrl(url)
        try:
            element = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".rc-AssignmentInstructions")),
            )
        except Exception as e:
            utils.log(e)

        time.sleep(3)

        header = self.driver.find_element_by_class_name("c-peer-review-title").text

        html_body = self.driver.find_element_by_id("main").get_attribute('outerHTML')

        res_html_instructions = "<!DOCTYPE html>\n<html lang=\"en\">\n <head>\n   <title>" + header + '</title>\n   <link rel="stylesheet" href="../../Resources/html/styles.css" />\n </head>\n<body>' + html_body + "\n</body>\n</html>"

        submissions_button = self.driver.find_elements_by_xpath("//a[contains(@class,'colored-tab')]")[1]
        submissions_button.click()

        try:
            element = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".rc-AssignmentSubmitEditView")),
            )
        except Exception as e:
            utils.log(e)

        time.sleep(3)

        html_body = self.driver.find_element_by_id("main").get_attribute('outerHTML')

        res_html_submission = "<!DOCTYPE html>\n<html lang=\"en\">\n <head>\n   <title>" + header + '</title>\n   <link rel="stylesheet" href="../../Resources/html/styles.css" />\n </head>\n<body>' + html_body + "\n</body>\n</html>"

        return header, res_html_instructions, res_html_submission

    ###################################################################################################################
    """" Driver Functions """
    ###################################################################################################################
    def loadUrl(self, url):
        self.driver.get(url)

    def loadHtml(self, html_content):
        self.driver.get("data:text/html;charset=utf-8," + html_content)

    def executeScript(self, script):
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            utils.log(e)
            return None

    def closeBrowser(self):
        self.driver.close()
        self.driver.quit()

