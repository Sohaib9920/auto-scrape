from pydantic import BaseModel
from selenium import webdriver
from src.dom.service import DomService, Element


class PageState(BaseModel):
    current_url: str
    page_title: str
    interactable_elements: list[Element]
    selector_map: dict[int, str]


class StateManager:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.dom_service = DomService(driver)

    def get_current_state(self, only_top: bool = True) -> PageState:
        current_content = self.dom_service.get_current_state(only_top)
        current_state = PageState(
            current_url=self.driver.current_url,
            page_title=self.driver.title,
            interactable_elements=current_content.interactable_elements,
            selector_map=current_content.selector_map
        )
        return current_state
    
    def add_change_info(self, current_state: PageState, previous_state: PageState) -> PageState:
        if previous_state is None:
            return current_state
        current_elements = current_state.interactable_elements
        previous_elements_content = [e.content for e in previous_state.interactable_elements]
        for elem in current_elements:
            if elem.content not in previous_elements_content:
                elem.addition = True
    
    def add_parent_info(self, current_state: PageState):
        selector_map = current_state.selector_map
        xpaths = selector_map.values()
        for elem in current_state.interactable_elements:
            elem_xpath = selector_map[elem.index]
            n_parents = sum(xpath in elem_xpath for xpath in xpaths if xpath != elem_xpath)
            elem.n_parents = n_parents
    

