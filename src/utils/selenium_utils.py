from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def setup_selenium_driver(headless: bool = False) -> webdriver.Chrome:
    # Configure Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")

    # Disable automation flags
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)

    return driver