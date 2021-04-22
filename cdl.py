import os
import re
import time
import getpass
import requests
import argparse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException


def downloadfile(topic, topic_count, title, url):
    filename = coursename + "/" + str(topic_count) + " " + topic + "/" + title + ".mp4"

    r = requests.get(url)
    f = open(filename, 'wb')
    for chunk in r.iter_content(chunk_size=255):
        if chunk:  # filter out keep-alive new chunks
            f.write(chunk)
    print(clean_title + ".mp4 download successfully!")
    f.close()


# parser = argparse.ArgumentParser()
# parser.add_argument("-t", "--time", type=float, default=10,
#                     help="Time for selenium web driver to wait for missing element(s) implicitly")

headless_mode_off = True

count = 1
waiting_time = 10

profile = webdriver.FirefoxProfile()
profile.set_preference("media.volume_scale", "0.0")
profile.update_preferences()

if headless_mode_off:
    browser = webdriver.Firefox(firefox_profile=profile)
else:
    # Operating in headless mode
    opts = Options()
    opts.set_headless()
    assert opts.headless
    browser = webdriver.Firefox(firefox_profile=profile, options=opts)

browser.implicitly_wait(waiting_time)
browser.get('https://www.coursera.org/?authMode=login')

courses = browser.find_elements_by_xpath("//h4[contains(@class,'headline-1-text')]")
# exit if login failed
# can be no courses found in the Last Active list also
if (len(courses) == 0):
    print("Wrong email or password. Please try again!")
    browser.quit()
    exit()

course = input("Please enter the coursename you want to download exactly as shown in the website: ")
coursename = course.replace("/", "")
coursename = coursename.replace("?", "")
coursename = coursename.replace(":", "-")

print("Searching for " + course + " ...")
found = False
for i in range(len(courses)):
    if course.lower() == courses[i].text.lower():
        found = True
        break

# exit program if the course doesn't exist in last active list
if not (found):
    print("Sorry, the course is not found in your Last Active list.")
    browser.quit()
    exit()

# click on course name
courses[i].click()

weeks = browser.find_elements_by_xpath("//div[contains(@class,'rc-NavigationDrawer')]/a")
print("Total week for this course: " + str(len(weeks)))

# loop through all weeks
topic_count = 1
for i in range(len(weeks)):
    weeks[i].click()
    time.sleep(waiting_time)  # longer wait time
    video_elem = browser.find_elements_by_xpath("//ul/li/a/div/div/div/div[contains(@class,'rc-WeekItemName')]/span")
    video = 0
    for z in range(len(video_elem)):
        if video_elem[z].text == "Lecture":
            video += 1
    print("Total video(s) in week " + str(i + 1) + ": " + str(video))

    # navigate to video page by click on the 1st video
    browser.find_element_by_xpath("//ul/li/a/div").click()

    topic_elem = browser.find_elements_by_xpath("//h3[contains(@class,'lesson-name')]")
    # expand all topic
    for j in range(1, len(topic_elem)):
        topic_elem[j].click()
    time.sleep(0.5)

    # browse topic
    for k in range(len(topic_elem)):
        try:
            topic = topic_elem[k].text
        except StaleElementReferenceException as Exception:
            topic_elem = browser.find_elements_by_xpath("//h3[contains(@class,'lesson-name')]")
            topic = topic_elem[k].text
            for j in range(1, len(topic_elem)):
                topic_elem[j].click()

        topic = topic.replace("/", "")
        topic = topic.replace("?", "")
        topic = topic.replace(":", "-")
        topic = topic.replace('"', "'")
        print("Browsing topic: " + topic)

        # count number of video in a topic
        video_elem2 = browser.find_elements_by_xpath("(//div[contains(@class,'item-list')])[" + str(
            k + 1) + "]/ul/li/a/div/div/div[contains(@class,'rc-NavItemName')]/span")
        video2 = 0
        for z in range(len(video_elem2)):
            if video_elem2[z].text == "Lecture":
                video2 += 1
        print("Number of video(s) under this topic: " + str(video2))

        if video2 > 0:
            path = coursename + "/" + str(topic_count) + " " + topic
            # check if the directory exist
            if not os.path.exists(path):
                os.makedirs(path)
                topic_count += 1
                # print("New folder created!\n")
            else:
                print("The folder already exist, download process terminated!")
                browser.quit()
                exit()

        v = 0
        counter = 1
        while v < video2:
            # navigate to video page
            browser.find_element_by_tag_name('body').send_keys(
                Keys.CONTROL + Keys.HOME)  # scroll to top to prevent element not clickable (blocked by other element)
            time.sleep(0.5)
            browser.find_element_by_xpath(
                "((//div[contains(@class,'rc-CollapsibleLesson')])[" + str(k + 1) + "]/div/ul/li)[" + str(
                    counter) + "]").click()
            counter += 1

            # prevent browser remains at the previous page (due to slow internet speed) and get the count of video as 1
            time.sleep(1)

            # check if a video exist in the page
            video_list = browser.find_elements_by_tag_name('video')
            # print(len(video_list))

            if len(video_list) > 0:
                if not (k == 0 and v == 0):
                    browser.find_element_by_tag_name('body').send_keys(
                        Keys.CONTROL + Keys.HOME)  # scroll to top to prevent element not clickable (blocked by navbar)
                    time.sleep(0.5)

                src = browser.find_element_by_xpath("//ul/span/li[contains(@class,'rc-LectureDownloadItem')]/a")
                src_link = src.get_attribute("href")
                title = browser.find_element_by_xpath("(//h4)")
                clean_title = title.text.replace("/", "")
                clean_title = clean_title.replace("?", "")
                clean_title = clean_title.replace(":", "-")
                clean_title = clean_title.replace('"', "'")
                clean_title = str(count) + " " + clean_title

                downloadfile(topic, topic_count - 1, clean_title, src_link)
                count += 1
                v += 1

            # close the modal if pop up
            modal = browser.find_elements_by_class_name("c-modal-overlay")
            if len(modal) > 0:
                browser.find_element_by_xpath("//div[contains(@class,'c-modal-x-out')]/a").click()
                time.sleep(0.5)

    browser.find_element_by_tag_name('body').send_keys(
        Keys.CONTROL + Keys.HOME)  # scroll to top to prevent element not clickable (blocked by navbar)
    time.sleep(0.5)
    # back to all week navigation
    browser.find_element_by_class_name("rc-BackToWeekButton").click()
    weeks = browser.find_elements_by_xpath("//div[contains(@class,'rc-NavigationDrawer')]/a")
    print("")

print("All videos for " + course + " have been downloaded successfully!")
browser.quit()