from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BrowserActions:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def search_google(self, query: str):
        self.driver.get(query)
        search_box = self.wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(query)
        search_box.submit()
    
    def go_to_url(self, url: str):
        self.driver.get(url)
    
    def click_element(self, identifier: dict):
        element = self._find_element(identifier)
        element.click()
    
    def _find_element(self, identifier: dict):
        for key, value in identifier.items():
            try:
                if key == "id":
                    return self.wait.until(
                        EC.presence_of_element_located((By.ID, value))
                    )
                elif key == "class":
                    return self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, value))
                    )
                elif key == "name":
                    return self.wait.until(
                        EC.presence_of_element_located((By.NAME, value))
                    )
                elif key == "text":
                    return self.wait.until(
                        EC.presence_of_element_located((By.XPATH, f"//*[text()[contains(., {value})]]"))
                    )
                elif key == "placeholder":
                    return self.wait.until(
                        EC.presence_of_element_located((By.XPATH, f"//*[@placeholder={value}]"))
                    )
            except:
                continue
        
        raise Exception("Element not found with provided identifiers")
