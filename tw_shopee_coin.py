import os
import pickle
import txt
import config
import exitCode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as OpsC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as OpsF
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager


class Browser:
    def __init__(self, name):
        if name == "firefox":
            options = OpsF()
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            options.set_preference("network.http.spdy.enabled.http2", False)
            self.driver = webdriver.Firefox(
                service=Service(GeckoDriverManager().install()),
                options=options,
            )
        elif name == "chrome":
            coptions = OpsC()
            coptions.add_argument("--headless")
            coptions.add_argument("--disable-notifications")
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(), chrome_options=coptions
            )
        self.driver.get(config.URL_LOGIN)
        self.wait = WebDriverWait(self.driver, config.TIMEOUT_OPERATION)


def tryLogin(browser, username, password):
    driver = browser.driver
    wait = browser.wait
    driver.get(config.URL_LOGIN)
    WebDriverWait(driver, 5).until(EC.url_changes(config.URL_LOGIN))
    curUrl = driver.current_url
    if curUrl == config.URL_COIN:
        print("Already logged in.")
        return
    else:
        print("Try to login by username and password.")
        inputUsername = wait.until(
            EC.presence_of_element_located((By.NAME, "loginKey"))
        )
        inputUsername.send_keys(username)
        inputPassword = wait.until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        inputPassword.send_keys(password)
        btnLogin = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='登入']"))
        )
        btnLogin.click()
        print("Login form submitted. Waiting for redirect.")

        xpath = f"//div[contains(text(),'{txt.WRONG_PASSWORDS[0]}') or contains(text(),'{txt.WRONG_PASSWORDS[1]}') or contains(text(),'{txt.WRONG_PASSWORDS[2]}') or contains(text(),'{txt.USE_LINK}') or contains(text(),'{txt.TOO_MUCH_TRY}') or contains(text(),'{txt.SHOPEE_REWARD}') or contains(text(),'{txt.EMAIL_AUTH}')] | //button[text()='{txt.PLAY_PUZZLE}']"
        result = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

        text = result.text
        print(text)

        t = driver.get_screenshot_as_file("result.png")
        print("截圖結果: %s" % t)
        if text == txt.SHOPEE_REWARD:
            # login succeeded
            print("Login succeeded.")
            return
        if text in txt.WRONG_PASSWORDS:
            # wrong password
            print("Login failed: wrong password.")
            return exitCode.WRONG_PASSWORD
        if text == txt.PLAY_PUZZLE:
            # need to play puzzle
            print("Login failed: I cannot solve the puzzle.")
            return exitCode.CANNOT_SOLVE_PUZZLE
        if text == txt.USE_LINK:
            # need to authenticate via SMS link
            print("Login failed: please login via SMS.")
            return exitCode.NEED_SMS_AUTH
        if text == txt.EMAIL_AUTH:
            # need to authenticate via email; this is currently not supported
            print("Login failed: need email Auth")
            return exitCode.NEED_EMAIL_AUTH


def tryReceiveCoin(browser):
    driver = browser.driver
    wait = browser.wait
    xpath = f"//button[contains(text(),'{txt.RECEIVE_COIN}') or contains(text(),'{txt.COIN_RECEIVED}')]"
    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    btnReceiveCoin = driver.find_element(By.XPATH, xpath)

    text = btnReceiveCoin.text
    if text.startswith(txt.COIN_RECEIVED):
        print("Coin already received.")
        return exitCode.ALREADY_RECEIVED
    btnReceiveCoin.click()
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, f"//button[contains(text(),'{txt.COIN_RECEIVED}')]")
        )
    )

    print("Coin received.")
    return exitCode.SUCCESS


def tryLoginWithSmsLink(browser):
    driver = browser.driver
    wait = browser.wait
    wait.until(
        EC.presence_of_element_located((By.XPATH, f"//div[text()='{txt.USE_LINK}']"))
    )
    btnLoginWithLink = driver.find_element(By.XPATH, f"//div[text()='{txt.USE_LINK}']")
    btnLoginWithLink.click()

    wait.until(EC.url_to_be("https://shopee.tw/verify/link"))

    try:
        driver.find_element(By.XPATH, f"//div[text()='{txt.TOO_MUCH_TRY}']")
        return exitCode.TOO_MUCH_TRY
    except:
        pass

    print(
        "An SMS message is sent to your mobile. Once you click the link I will keep going. I will wait for you and please complete it in 10 minutes."
    )

    result = "none"
    try:
        success = WebDriverWait(driver, config.TIMEOUT_SMS_AUTH).until(
            EC.url_matches(r"^https:\/\/shopee.tw\/shopee-coins(\?.*)?$")
            or EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//div[contains(text(),'{txt.FAILURE}') or contains(text(),'{txt.FAILURE2}')]",
                )
            )
        )
        result = "success"
        if txt.FAILURE in success.text:
            return exitCode.TOO_MUCH_TRY
        elif txt.FAILURE2 in success.text:
            return exitCode.TOO_MUCH_TRY
    except:
        pass

    if result == "success":
        print("Login permitted.")
        return

    print("Login denied.")
    return exitCode.LOGIN_DENIED


def loadCookies(browser):
    if os.path.exists("cookies.pkl"):
        browser.driver.get(config.URL_HOME)
        with open("cookies.pkl", "rb") as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                browser.driver.add_cookie(cookie)
    return browser


def saveCookies(browser):
    with open("cookies.pkl", "wb") as filehandler:
        pickle.dump(browser.driver.get_cookies(), filehandler)


def runBot(args):
    os.environ["GH_TOKEN"] = args.GH_TOKEN

    browser = loadCookies(Browser("firefox"))

    result = tryLogin(browser, args.username, args.password)

    if result == exitCode.NEED_SMS_AUTH:
        result = tryLoginWithSmsLink(browser)

    if result != None:
        return result

    result = tryReceiveCoin(browser)
    saveCookies(browser)
    return result
