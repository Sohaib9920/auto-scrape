from dotenv import load_dotenv
from src.llm.service import LLM, AvailableModel
from src.actions.browser_actions import Action
from tokencost import calculate_prompt_cost, count_string_tokens


class PlaningAgent:
    def __init__(self, task: str, default_actions: str, model: AvailableModel):
        load_dotenv()
        self.model = model
        self.llm = LLM(model=self.model)
        self.system_prompt = [
            {"role": "system", "content": self.get_system_prompt(task, default_actions)}
        ]
        self.messages = []
        self.messages_all = []
        self.input_messages = None

    def chat(self, text: str, skip_call: bool = False) -> Action:
        input_messages = (
            self.system_prompt + self.messages + [{"role": "user", "content": text}]
        )
        self.input_messages = input_messages
        try:
            # Calculate total cost for all messages
            total_cost = calculate_prompt_cost(input_messages, self.model)
            total_tokens = count_string_tokens(
                " ".join([m["content"] for m in input_messages]), self.model
            )
            print(
                "Total prompt cost: ",
                f"${total_cost:,.2f}",
                "Total tokens: ",
                f"{total_tokens:,}",
            )
        except Exception as e:
            print(f"Error calculating prompt cost: {e}")

        if skip_call:
            return Action(action="nothing")

        response = self.llm.create_chat_completion(input_messages, Action)

        pre_action_msg = {"role": "user", "content": "... execute action ..."}
        self.messages.append(pre_action_msg)
        self.messages_all.append(pre_action_msg)

        action_msg = {"role": "assistant", "content": response.model_dump_json()}
        self.messages.append(action_msg)
        self.messages_all.append(action_msg)

        if len(self.messages) > 20:
            self.messages = self.messages[-20:]

        return response

    def get_system_prompt(self, task: str, default_actions: str) -> str:

        output_format = """
{"action": "action_name", "params": {"param_name": "param_value"}, "goal": "short description what you want to achieve", "valuation_previous_goal": "Success if completed, else short sentence of why not successful."}
"""

        AGENT_PROMPT =f"""
You are an AI agent that helps users navigate websites and perform actions.

## Task:
{task}

## Available actions:
At each step, you must choose an action from the predefined set of actions in the format:  
{{name: arguments_definition}}
The available actions are:  
{default_actions}  

## Input:
The page content will be provided as numbered elements like this:
0:<button>Click me</button>
1:<a href="/test">Link text</a>
2:Some visible text content 

Additionally you get sequence of previous actions.

## Instructions:
- Provide your next action based on the available actions, previous actions and visible elements. 
- Make sure to follow action's argument_definition.
- Make sure task is completed before 'done' action.
- Each element has a unique index that can be used to interact with it. To interact with elements, use their index number in the click() or input() actions. Make 100% sure that the index is ALWAYS present if you use the click() or input() actions.
- Validate if previous goal was successfully achieved without violating any task requirements. If it wasn't, take the necessary next action to correct it or move closer to completing the goal.
- Do not repeat the same action again and again. If you get stuck, try to find a new element that can help you achieve your goal or if persistent, go back or reload the page.
- Do not interact with ADS.
- Respond with a valid JSON object containing the action and any required parameters and your current goal of this action.

## Response format:
{output_format}

"""

        return AGENT_PROMPT
