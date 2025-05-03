from dotenv import load_dotenv
from src.llm.service import LLM, AvailableModel
from src.actions.browser_actions import Action
from tokencost import calculate_all_costs_and_tokens
import decimal
from src.state_manager.utils import save_conversation, encode_image


class PlaningAgent:
    def __init__(self, default_actions: str, model: AvailableModel):
        load_dotenv()
        self.model = model
        self.llm = LLM(model=self.model)
        self.system_prompt = [
            {"role": "system", "content": self.get_system_prompt(default_actions)}
        ]
        self.messages = []
        self.messages_all = []

    def chat(
        self, text: str, store_conversation: str = "", image: str = ""
    ) -> Action:
        
        if image:
            combined_input = [
                {'type': 'text', 'text': text},
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:image/png;base64,{encode_image(image)}',
                    },
                },
            ]
        else:
            combined_input = [{'type': 'text', 'text': text}]
        
        input_messages = (
			self.system_prompt + self.messages + [{'role': 'user', 'content': combined_input}]
		)

        response: Action = self.llm.create_chat_completion(input_messages, Action)

        if store_conversation:
            save_conversation(
                input_messages, response.model_dump_json(), store_conversation
            )

        action_msg = {"role": "assistant", "content": response.model_dump_json()}
        self.messages.append(action_msg)
        self.messages_all.append(action_msg)

        try:
            output = calculate_all_costs_and_tokens(
				self.system_prompt + self.messages + [{'role': 'user', 'content': text}],
				response.model_dump_json(),
				self.model,
			)
            if image:
                # resolution 1512 x 767
                image_cost = 0.000213
                total_cost = (
                    output['prompt_cost']
                    + output['completion_cost']
                    + decimal.Decimal(str(image_cost))
                )
                print(
                    f'Text ${output["prompt_cost"]:,.4f} + Image ${image_cost:,.4f} = ${total_cost:,.4f} for {output["prompt_tokens"] + output["completion_tokens"]}  tokens'
                )
            else:
                total_cost = output['prompt_cost'] + output['completion_cost']
                print(
                    f'Total cost: ${total_cost:,.4f} for {output["prompt_tokens"] + output["completion_tokens"]} tokens'
                )

        except Exception as e:
            print(f'Error calculating prompt cost: {e}')

        if len(self.messages) > 20:
            self.messages = self.messages[-20:]

        return response

    def add_user_prompt(self, text: str, after_system: bool = False):
        if after_system:
            self.system_prompt.append({"role": "user", "content": text})
        else:
            self.messages.append({"role": "user", "content": text})

    def get_system_prompt(self, default_actions: str) -> str:

        output_format = """
{"valuation_previous_goal": "Success if completed, else short sentence explaining why not successful.", "goal": "short description of what you want to achieve", "action": "action_name", "params": {"param_name": "param_value"}}
"""

        AGENT_PROMPT = f"""
You are an AI agent designed to assist users in navigating websites and performing actions efficiently.

## Available actions:
At each step, you must select an action from the predefined set of actions in the format:  
{{name: arguments_definition}}  
The available actions are:  
{default_actions}  

## Input:
Your input consists of all interactive elements on the current page, from which you can choose to click or input. They will be provided like this:  
      0:<button>Click me</button>  
      1:<a href="/test">parent link text</a> 
      3:    <a href="/check">child link text</a>
      _:Some visible text content  
(+) 100:<div>Suggested option: New York (JFK)</div>  
(+) 120:<input type="text" value="2025-04-15" aria-label="Departure date">  

- Elements prefixed with (+) indicate they were added or modified by the previous action (e.g., (+) 3:<div>Suggested option: New York (JFK)</div>). Pay attention to these as they may be relevant to your next step.  
- You also receive a sequence of previous actions to inform your decision-making.

## Instructions:
- Determine your next action based on the available actions, previous actions, and visible elements, prioritizing (+) elements when they align with your goal.
- After `input()` action, must select from list of suggestions if it appeared even when field's `value` attribute is filled. Check (+) elements if suggestions appeared. DO NOT move to other field before confirming one field. 
- Before performing an action, check if any prerequisite steps (e.g., entering data before submitting, clicking a button to reveal a field) are required by the task. Address missing prerequisites first.
- Validate whether the previous goal was achieved successfully without skipping required steps. If a step was missed, take the necessary action to correct it before proceeding.
- For the `search_google` action, ensure the parameter is text and not a URL.
- Each element has a unique index (e.g., 0, 1, 385). Always include the index in `click()` or `input()` actions—double-check its presence to avoid errors.
- Avoid repeating the same action consecutively. If stuck, explore new elements that might help, or use `ask_user` for clarification.
- Trigger the `done` action immediately upon task completion, preceded by a single `send_user_text` message to inform the user of the results.
- Utilize `send_user_text` solely for delivering informational messages to the user. Use `ask_user` whenever user input is needed.
- Avoid redundant use of `send_user_text` in responses.
- Do not interact with advertisements or elements clearly marked as ads.

## Response format:
{output_format}
"""
        return AGENT_PROMPT
