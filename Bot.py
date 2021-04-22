from selenium import webdriver
import os
import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Bot:
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

    def getWeeks(self):
        try:
            element = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".week-number"))
            )
        except Exception as e:
            utils.log(e)

        weeks = self.driver.find_elements_by_xpath("//div[contains(@class, 'rc-WeekCollectionNavigationItem')]//div[contains(@class, 'rc-NavigationDrawer')]//a[contains(@class,'rc-WeekNavigationItem')]")

        result = []

        for week in weeks:
            week_title = week.get_attribute("innerText")
            week_url = week.get_attribute("href")
            # print(week_title)
            # print(week_url)
            result.append({"title": week_title, "url": week_url})

        return result

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

