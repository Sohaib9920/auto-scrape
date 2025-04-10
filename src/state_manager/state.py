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
        current_content = self.dom_service.get_current_state(only_top)
        current_state = PageState(
            current_url=self.driver.current_url,
            page_title=self.driver.title,
            interactable_elements=current_content.output_string,
            selector_map=current_content.selector_map
        )
        return current_state
    
    def get_compared_elements(self, current_state: PageState, previous_state: PageState) -> str:
        if previous_state is None:
            return current_state.interactable_elements
        sep = "\n"
        current_elements = current_state.interactable_elements.split(sep)
        previous_elements_ = [e[e.find(":")+1:] for e in previous_state.interactable_elements.split(sep)]
        compared_current_elements = []
        for elem in current_elements:
            if elem[elem.find(":")+1:] not in previous_elements_:
                compared_current_elements.append("(+) " + elem)
            else:
                compared_current_elements.append(elem)
        return sep.join(compared_current_elements)
