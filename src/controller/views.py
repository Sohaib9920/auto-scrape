from src.browser.views import BrowserState
from typing import Literal, Optional
from pydantic import BaseModel


class SearchGoogleControllerAction(BaseModel):
	query: str


class GoToUrlControllerAction(BaseModel):
	url: str


class ClickElementControllerAction(BaseModel):
	id: int


class InputTextControllerAction(BaseModel):
	id: int
	text: str


class DoneControllerAction(BaseModel):
	text: str


class ControllerActions(BaseModel):
    search_google: Optional[SearchGoogleControllerAction] = None
    go_to_url: Optional[GoToUrlControllerAction] = None
    nothing: Optional[Literal[True]] = None
    go_back: Optional[Literal[True]] = None
    done: Optional[DoneControllerAction] = None
    click_element: Optional[ClickElementControllerAction] = None
    input_text: Optional[InputTextControllerAction] = None

    @staticmethod
    def description() -> str:
	    return """
- Search Google with a query
  Example: {"search_google": {"query": "weather today"}}
- Navigate directly to a URL
  Example: {"go_to_url": {"url": "https://abc.com"}}
- Do nothing/wait
  Example: {"nothing": true}
- Go back to previous page
  Example: {"go_back": true}
- Mark entire task as complete
  Example: {"done": {"text": "This is the requested result of the task..."}}
- Click an element by its ID
  Example: {"click_element": {"id": 1}}
- Input text into an element by its ID
  Example: {"input_text": {"id": 1, "text": "Hello world"}}
"""


class ControllerActionResult(BaseModel):
	done: bool
	error: Optional[str] = None


class ControllerPageState(BrowserState):
	screenshot: Optional[str] = None
	
