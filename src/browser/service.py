from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from src.browser.views import BrowserState
from src.dom.service import DomService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time


class BrowserService:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver: webdriver.Chrome | None = None
        self.MAXIMUM_WAIT_TIME = 30
        self.current_state = None

    def init(self) -> webdriver.Chrome:
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')

        # Anti-detection measures
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-infobars')

        # Initialize the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()

        self.driver = driver
        return driver
	
    def _get_driver(self) -> webdriver.Chrome:
        if self.driver is None:
            self.driver = self.init()
        return self.driver
    
    def close(self):
        driver = self._get_driver()
        driver.quit()
        self.driver = None

    def __del__(self):
        if self.driver is not None:
            self.close()
    
    def wait_for_page_load(self):
        driver = self._get_driver()
        check_interval=1

        def is_dom_stable(driver):
            initial_dom = driver.execute_script("return document.documentElement.outerHTML")
            time.sleep(check_interval)
            current_dom = driver.execute_script("return document.documentElement.outerHTML")
            return initial_dom == current_dom

        WebDriverWait(driver, self.MAXIMUM_WAIT_TIME).until(is_dom_stable)
    
    def get_updated_state(self) -> BrowserState:
        start_time = time.time()

        driver = self._get_driver()
        dom_service = DomService(driver)
        dom_content = dom_service.get_current_state()
        self.current_state = BrowserState(
			items=dom_content.items,
			selector_map=dom_content.selector_map,
			url=driver.current_url,
			title=driver.title,
		)

        elapsed_time = time.time() - start_time
        print(f'get_updated_state took {elapsed_time:.2f} seconds')
        return self.current_state
    
    # region - Browser Actions

    def search_google(self, query: str):
        driver = self._get_driver()
        driver.get(f'https://www.google.com/search?q={query}')
        self.wait_for_page_load()

    def go_to_url(self, url: str):
        driver = self._get_driver()
        driver.get(url)
        self.wait_for_page_load()

    def go_back(self):
        driver = self._get_driver()
        driver.back()
        self.wait_for_page_load()

    def refresh(self):
        driver = self._get_driver()
        driver.refresh()
        self.wait_for_page_load()
    
    def done(self, text: str):
        print(f'Done on page {self.current_state.url}\n\n: {text}')
        return text
    
    def take_screenshot(self) -> str:
        driver = self._get_driver()
        screenshot = driver.get_screenshot_as_base64()
        return screenshot
    
    def _webdriver_wait(self):
        driver = self._get_driver()
        return WebDriverWait(driver, 10)
    
    def click_element_by_index(self, index: int, state: BrowserState):
        xpath = state.selector_map[index]
        self._click_element_by_xpath(xpath)
    
    def _click_element_by_xpath(self, xpath: str):
        driver = self._get_driver()
        wait = self._webdriver_wait()

        try:
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            time.sleep(0.5)
            element.click()
            self.wait_for_page_load()
            
        except Exception as e:
            raise Exception(f'Failed to click element with xpath: {xpath}. Error: {str(e)}')
    
    def input_text_by_index(self, index: int, text: str, state: BrowserState):
        xpath = state.selector_map[index]
        self._input_text_by_xpath(xpath, text)
    
    def _input_text_by_xpath(self, xpath: str, text: str):
        driver = self._get_driver()
        wait = self._webdriver_wait()

        try:
            element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            time.sleep(0.5)
            element.clear()
            element.send_keys(text)
            self.wait_for_page_load()
            
        except Exception as e:
            raise Exception(
				f'Failed to input text into element with xpath: {xpath}. Error: {str(e)}'
			)