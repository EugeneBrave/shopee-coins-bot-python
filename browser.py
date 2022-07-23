import config
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options as OpsC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as OpsF
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
        elif name == "remote":
            roptions = webdriver.ChromeOptions()
            roptions.add_argument("--headless")
            roptions.add_argument("--disable-notifications")
            self.driver = webdriver.Remote(
                command_executor='http://192.168.11.8:4444',
                options=roptions
            )
        self.driver.get(config.URL_LOGIN)
        self.wait = WebDriverWait(self.driver, config.TIMEOUT_OPERATION)