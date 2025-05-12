from langchain_core.messages import HumanMessage, SystemMessage
from src.controller.views import ControllerPageState


class AgentSystemPrompt:
	def __init__(self, task: str, default_action_description: str):
		self.task = task
		self.default_action_description = default_action_description

	def get_system_message(self) -> SystemMessage:
		AGENT_PROMPT = f"""
## Input:
Your input consists of all interactive elements on the current page, from which you can choose to click or input. They will be provided in the following format:  
      0:<button>Click me</button>  
      1:<a href="/test">parent link text</a>  
      3:<a href="/check">child link text</a>  
      _:Some visible text content  
(+) 100:<div>Suggested option: New York (JFK)</div>  
(+) 120:<input type="text" value="2025-04-15" aria-label="Departure date">  

- Elements prefixed with (+) indicate they were added or modified by the previous action (e.g., (+) 100:<div>Suggested option: New York (JFK)</div>). Pay special attention to these, as they may be relevant to your next step.  
- You will also receive a sequence of previous actions to inform your decision-making.

Available actions (choose EXACTLY ONE — not 0 or 2):  
{self.default_action_description}

## Instructions:
- If a picture is provided, use it to understand the context and determine the next action.  
- After an `input()` action, if a list of suggestions appears (even if the field’s `value` is already filled), you MUST select from the suggestions. Always check for (+) elements to confirm this. Do NOT move to another field before confirming the current one.  
- Before performing any action, verify whether prerequisite steps are needed (e.g., entering data before clicking submit, or clicking a button to reveal a field). Handle prerequisites first.  
- Check whether the previous goal was successfully completed. If not, correct it before proceeding.  
- Trigger the `done` action immediately upon task completion.
- Do NOT interact with advertisements or elements clearly marked as ads.
- Avoid repeating the same action again and again. If stuck, explore new elements that might help.

## Output:
Respond with a valid JSON object containing the following fields:
- valuation_previous_goal: A brief evaluation of the previous goal — either what was achieved or what went wrong.  
- memory: A field for storing relevant context or task progress (e.g., storing already found jobs if the goal is to find 10 jobs).  
- next_goal: A short description of the next goal to achieve.  
- action: Your next action to achieve the next_goal.
"""
		return SystemMessage(content=AGENT_PROMPT)


class AgentMessagePrompt:
	def __init__(self, state: ControllerPageState):
		self.state = state

	def get_user_message(self) -> HumanMessage:
		state_description = f"""
Current url: {self.state.url}
Interactive elements:
{self.state.dom_items_to_string()}
        """

		if self.state.screenshot:
			# Format message for vision model
			return HumanMessage(
				content=[
					{'type': 'text', 'text': state_description},
					{
						'type': 'image_url',
						'image_url': {'url': f'data:image/png;base64,{self.state.screenshot}'},
					},
				]
			)

		return HumanMessage(content=state_description)

	def get_message_for_history(self) -> HumanMessage:
		return HumanMessage(content=f'Currently on url: {self.state.url}')


