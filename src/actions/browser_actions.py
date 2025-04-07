from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional
import time


class ActionParams(BaseModel):
    url: Optional[str] = None
    id: Optional[int] = None
    text: Optional[str] = None


class Action(BaseModel):
    action: str
    params: Optional[ActionParams] = None
    goal: str
    valuation_previous_goal: str


class BrowserActions:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.selector_map: dict[int, str] = {}

    def update_selector_map(self, selector_map: dict[int, str]):
        self.selector_map = selector_map

    def execute_action(self, action: Action, selector_map: dict[int, str]):
        print(action.model_dump_json(indent=4))
        action_name = action.action
        self.update_selector_map(selector_map)

        if action_name == "search_google":
            if action.params and action.params.text:
                self.search_google(action.params.text)
            else:
                raise Exception("text is required for search_google action")

        elif action_name == "nothing":
            pass

        elif action_name == "go_to_url":
            if action.params and action.params.url:
                self.go_to_url(action.params.url)
            else:
                raise Exception("Url is required for go_to_url action")

        elif action_name == "go_back":
            self.go_back()

        elif action_name == "done":
            return True

        elif action_name == "input":
            if action.params and action.params.id and action.params.text:
                self.input(action.params.id, action.params.text)
            else:
                raise Exception("Id and text are required for input action")

        elif action_name == "click":
            if action.params and action.params.id:
                self.click(action.params.id)
            else:
                raise Exception("Id is required for click action")

        else:
            raise Exception(f"Action {action_name} not found")

    def click(self, id: int):
        xpath = self.selector_map.get(id)
        if xpath is None:
            raise ValueError(f"No selector found for id {id}")
        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            element,
        )
        time.sleep(0.5)
        element.click()

    def input(self, id: int, text: str):
        xpath = self.selector_map.get(id)
        if xpath is None:
            raise ValueError(f"No selector found for id {id}")
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            element,
        )
        time.sleep(0.5)
        element.clear()
        element.send_keys(text)

    def search_google(self, query: str):
        self.driver.get("https://www.google.com/")
        search_bar = self.wait.until(EC.presence_of_element_located((By.NAME, "q")))
        search_bar.send_keys(query)
        search_bar.submit()

    def go_to_url(self, url: str):
        self.driver.get(url)

    def go_back(self):
        self.driver.back()

    def get_default_actions(self) -> dict[str, str]:
        return {
            "search_google": "text: string",
            "go_to_url": "url: string",
            "done": "",
            "go_back": "",
            "click": "id: int",
            "input": "id: int, text: string",
            "nothing": "",
        }
