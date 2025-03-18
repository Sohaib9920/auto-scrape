from pydantic import BaseModel
from selenium import webdriver
from src.dom.service import DomService


class PageState(BaseModel):
    current_url: str
    page_title: str
    interactable_elements: str
    selector_map: dict[int, str]


class StateManager:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.dom_service = DomService(driver)

    def get_current_state(self, only_top: bool = True) -> PageState:
        processed_content = self.dom_service.get_current_state(only_top)
        return PageState(
            current_url=self.driver.current_url,
            page_title=self.driver.title,
            interactable_elements=processed_content.output_string,
            selector_map=processed_content.selector_map
        )