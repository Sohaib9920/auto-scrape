from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
import time

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# options.add_argument("--headless")

options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options)
# stealth(driver,
#         languages=["en-US", "en"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True,
# )

# driver = uc.Chrome(options=options, headless=False)

# url = 'https://www.google.com/travel/flights'
# url = "https://www.kayak.com/flights"
# url = "https://docs.google.com/spreadsheets/d/1iwaV2GmQPZcyMWwxZu-rGPEIzo-Ac7j_rFslLXqVjok/edit?usp=sharing"
url = "https://groq.com/pricing/"
driver.get(url)

try:
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Accept' or text()='Accept all']"), )
    )
    accept_button.click()
except:
    print("No accept button found")

time.sleep(10)

driver.quit()
