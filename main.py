from driver import Driver
from bot import Bot
import json
import os
import utils

if __name__ == '__main__':
    root = "I:\\Others\\Downloads\\Coursera\\Google Project Management\\Test"
    course_url = "https://www.coursera.org/learn/project-execution-google/home/welcome"

    driver = Driver("main")
    bot = Bot(driver, course_url, root, start_week=1)
    bot.run()

    driver.closeBrowser()

    print("end")


