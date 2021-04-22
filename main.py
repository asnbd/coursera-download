from Bot import Bot

if __name__ == '__main__':
    homeUrl = "https://www.coursera.org/learn/project-execution-google/home/welcome"

    bot = Bot("main")

    bot.loadUrl(homeUrl)
    print(bot.getWeeks())
    bot.closeBrowser()

    print("main")

