from selenium import webdriver
from selenium.webdriver.common.by import By

class StateManager:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def get_current_state(self):
        return {
            "current_url": self.driver.current_url,
            "interactable_elements": self.get_interactable_elements()
        }
    
    def get_interactable_elements(self) -> list[dict]:
        interactable_elements = [] 

        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            interactable_elements.append({
                "id": button.get_attribute("id"),
                "class": button.get_attribute("class"),
                "text": button.text
            })

        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        for input_field in inputs:
            interactable_elements.append({
                "id": input_field.get_attribute("id"),
                "class": input_field.get_attribute("class"),
                "placeholder": input_field.get_attribute("placeholder")
            })

        return interactable_elements