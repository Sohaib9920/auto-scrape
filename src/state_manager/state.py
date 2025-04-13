from pydantic import BaseModel
from selenium import webdriver
from src.dom.service import DomService, Element
from Screenshot import Screenshot


class PageState(BaseModel):
    current_url: str
    page_title: str
    interactable_elements: list[Element]
    selector_map: dict[int, str]
    screenshot: str


class StateManager:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.dom_service = DomService(driver)
        self.ob = Screenshot.Screenshot()

    def get_current_state(
            self, run_folder: str, only_top: bool = True, full_page_screenshot: bool = False, step: int = 0
        ) -> PageState:
        current_content = self.dom_service.get_current_state(only_top)

        if full_page_screenshot:
            # First load upto 10000 height of page then go top and then keep scrolling and taking screenshots
            current_positon = self.driver.execute_script("return [window.scrollX, window.scrollY]")
            self.ob.full_screenshot(
                driver=self.driver,
                save_path=run_folder,
                image_name=f'selenium_full_screenshot_{step}.png',
                is_load_at_runtime=True,
                load_wait_time=1,
            )
            self.driver.execute_script("window.scrollTo(arguments[0][0], arguments[0][1])", current_positon)
            screenshot = run_folder + f'/selenium_full_screenshot_{step}.png'
        else:
            file_name = run_folder + f'/window_screenshot_{step}.png'
            screenshot = self.driver.get_screenshot_as_file(file_name)
            screenshot = file_name if screenshot else ''


        current_state = PageState(
            current_url=self.driver.current_url,
            page_title=self.driver.title,
            interactable_elements=current_content.interactable_elements,
            selector_map=current_content.selector_map,
            screenshot=screenshot
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
    

