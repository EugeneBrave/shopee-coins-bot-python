import os, pickle, config

def loadCookies(browser, cookiePath):
    if os.path.exists(f"{cookiePath}/cookies.pkl"):
        browser.driver.get(config.URL_HOME)
        with open(f"{cookiePath}/cookies.pkl", "rb") as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                browser.driver.add_cookie(cookie)
    return browser


def saveCookies(browser, cookiePath):
    with open(f"{cookiePath}/cookies.pkl", "wb") as filehandler:
        pickle.dump(browser.driver.get_cookies(), filehandler)