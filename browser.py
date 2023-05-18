import config
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options as OpsC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as OpsF
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
import json

def send(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({'cmd': cmd, 'params': params})
    response = driver.command_executor._request('POST', url, body)
    return response.get('value')

def add_script(driver, script):
    send(driver, "Page.addScriptToEvaluateOnNewDocument", {"source": script})

WebDriver.add_script = add_script

class Browser:
    def __init__(self, name, ip=""):
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
        elif name == "remote":
            roptions = webdriver.ChromeOptions()
            prefs = {"profile.default_content_setting_values.notifications" : 2}
            roptions.add_experimental_option("prefs",prefs)
            roptions.add_argument("--disable-blink-features=AutomationControlled")
            # 消除webdriver特性
            self.driver = webdriver.Remote(
                command_executor=ip,
                options=roptions
            )
            self.driver.add_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """)
            # 在控制台中驗證window.navigator.webdriver的值為undefined。
        self.driver.get(config.URL_LOGIN)
        self.wait = WebDriverWait(self.driver, config.TIMEOUT_OPERATION)
