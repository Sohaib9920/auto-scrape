from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional
import urllib
import time


class ActionParams(BaseModel):
    url: Optional[str] = None
    id: Optional[int] = None
    text: Optional[str] = None


class Action(BaseModel):
    valuation_previous_goal: str
    goal: str
    action: str
    params: Optional[ActionParams] = None


class ActionResult(BaseModel):
    done: bool = False
    user_input: str = ""
    error: Optional[str] = None


class BrowserActions:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.selector_map: dict[int, str] = {}

    def update_selector_map(self, selector_map: dict[int, str]):
        self.selector_map = selector_map

    def execute_action(
        self, action: Action, selector_map: dict[int, str]
    ) -> ActionResult:
        print(action.model_dump_json(indent=4))
        action_name = action.action
        self.update_selector_map(selector_map)

        output = ActionResult()

        try:
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
                    raise Exception("url is required for go_to_url action")

            elif action_name == "go_back":
                self.go_back()

            elif action_name == "done":
                output.done = True

            elif action_name == "input":
                if action.params and action.params.id and action.params.text:
                    self.input(action.params.id, action.params.text)
                else:
                    raise Exception("id and text are required for input action")

            elif action_name == "click":
                if action.params and (action.params.id or action.params.id == 0):
                    self.click(action.params.id)
                else:
                    raise Exception("id is required for click action")

            elif action_name == "ask_user":
                if action.params and action.params.text:
                    output.user_input = self.ask_user(action.params.text)
                else:
                    raise Exception("text is requered for ask_user action")
                
            elif action_name == 'send_user_text':
                if action.params and action.params.text:
                    self.send_user_text(action.params.text)
                else:
                    raise Exception('text is required for send_user_text action')

            else:
                raise Exception(f"Action {action_name} not found")

        except Exception as e:
            output.error = str(e)

        return output

    def ask_user(self, question: str):
        print(question)
        print("--------------------------------\nInput: \n ")
        user_input = input()
        return user_input

    def click(self, id: int):
        xpath = self.selector_map.get(id)
        if xpath is None:
            raise ValueError(f"No selector found for id {id}")
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                element,
            )
            time.sleep(0.5)
            element.click()
        except Exception as e:
            print(f"Failed to click element. Error: {str(e)}")
            raise Exception(f"Failed to click element with index {id}, xpath: {xpath}")

    def input(self, id: int, text: str):
        xpath = self.selector_map.get(id)
        if xpath is None:
            raise ValueError(f"No selector found for id {id}")
        try:
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                element,
            )
            time.sleep(0.5)
            element.clear()
            element.send_keys(text)
        except Exception as e:
            raise Exception(
                f"Failed to input text into element with index {id}, xpath: {xpath}. Error: {str(e)}"
            )

    def search_google(self, query: str):
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        self.driver.get(search_url)

    def go_to_url(self, url: str):
        self.driver.get(url)

    def go_back(self):
        self.driver.back()
    
    def send_user_text(self, text: str):
        print(text)
        print('--------------------------------')

    def get_default_actions(self) -> dict[str, str]:
        return {
            "ask_user": "text: string",
            "send_user_text": "text: string",
            "search_google": "text: string",
            "go_to_url": "url: string",
            "done": "",
            "go_back": "",
            "click": "id: int",
            "input": "id: int, text: string",
            "nothing": "",
        }
