from src.browser.service import BrowserService
from src.browser.views import BrowserState
from src.controller.views import ControllerActionResult, ControllerActions, ControllerPageState


class ControllerService:
    def __init__(self):
        self.browser = BrowserService()
        self.browser_state: BrowserState = None
    
    def get_current_state(self, screenshot: bool = False) -> ControllerPageState:
        browser_state = self.browser.get_updated_state()
        self.browser_state = browser_state

        screenshot_b64 = None
        if screenshot:
            screenshot_b64 = self.browser.take_screenshot()

        return ControllerPageState(
            items=browser_state.items,
            url=browser_state.url,
            title=browser_state.title,
            selector_map=browser_state.selector_map,
            screenshot=screenshot_b64,
        )
    
    def act(self, action: ControllerActions) -> ControllerActionResult:
        try:
            if action.search_google:
                self.browser.search_google(action.search_google.query)
            elif action.go_to_url:
                self.browser.go_to_url(action.go_to_url.url)
            elif action.nothing:
                pass
            elif action.go_back:
                self.browser.go_back()
            elif action.done:
                self.browser.done(action.done.text)
                return ControllerActionResult(done=True)
            elif action.click_element:
                self.browser.click_element_by_index(
                    action.click_element.id, self.browser_state
                )
            elif action.input_text:
                self.browser.input_text_by_index(
                    action.input_text.id, action.input_text.text, self.browser_state
                )
            else:
                raise ValueError(f'Unknown action: {action}')

            return ControllerActionResult(done=False)

        except Exception as e:
            return ControllerActionResult(done=False, error=str(e))