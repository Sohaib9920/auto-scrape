from pydantic import BaseModel
from selenium import webdriver
from src.dom.service import DomService, ProcessedDomContent
from Screenshot import Screenshot


class PageState(BaseModel):
    current_url: str
    page_title: str
    dom_content: ProcessedDomContent
    screenshot: str


class StateManager:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.dom_service = DomService(driver)
        self.ob = Screenshot.Screenshot()

    def get_current_state(
            self, run_folder: str = "temp", full_page_screenshot: bool = False, step: int = 0
        ) -> PageState:
        dom_content = self.dom_service.get_current_state()

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
            dom_content=dom_content,
            screenshot=screenshot
        )

        return current_state
    
    def add_change_info(self, current_state: PageState, previous_state: PageState) -> PageState:
        if previous_state is None:
            return current_state
        current_elements = current_state.dom_content.items
        previous_elements_text = [e.text for e in previous_state.dom_content.items]
        for elem in current_elements:
            if elem.text not in previous_elements_text:
                elem.addition = True

    

