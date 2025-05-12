from pydantic import BaseModel
from typing import Optional
from src.controller.views import ControllerActions


class AskHumanAgentAction(BaseModel):
	question: str


class AgentOnlyAction(BaseModel):
	valuation_previous_goal: str
	memory: str
	next_goal: str

	ask_human: Optional[AskHumanAgentAction] = None

	@staticmethod
	def description() -> str:
		return """
- Ask human for help
  Example: {"ask_human": {"question": "To clarify ..."}}
"""


class AgentAction(ControllerActions, AgentOnlyAction):
	@staticmethod
	def description() -> str:
		return AgentOnlyAction.description() + ControllerActions.description()