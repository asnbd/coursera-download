from selenium import webdriver
import os
import utils


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

