from selenium import webdriver

class ActionValidator:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
    
    def is_action_successful(self, action: dict) -> bool:
        pass
    
    def check_ambiguity(self, action: dict) -> bool:
        pass