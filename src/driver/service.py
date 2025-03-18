from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class DriverService:
    def __init__(self, headless: bool = False, maximize_window: bool = True):
        self.headless = headless
        self.maximize_window = maximize_window

    def get_driver(self) -> webdriver.Chrome:
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")

        # Disable automation flags
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=chrome_options)
        if self.maximize_window:
            driver.maximize_window()

        return driver
