from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from src.controller.service import ControllerService
from src.agent.prompts import AgentMessagePrompt, AgentSystemPrompt
from src.agent.views import AgentAction
from src.controller.views import ControllerActionResult, ControllerPageState
from src.utils import store_conversation

load_dotenv()

class AgentService:
    def __init__(
        self, task: str, llm: BaseChatModel, 
        controller: ControllerService | None = None, use_vision: bool = False,
    ):       
        self.controller = controller or ControllerService()
        self.use_vision = use_vision
        self.llm = llm.with_structured_output(AgentAction)

        system_prompt = AgentSystemPrompt(
            task, default_action_description=AgentAction.description()
        ).get_system_message()
        print(system_prompt)
        first_message = HumanMessage(content=f'Your main task is: {task}')

        self.messages: list[BaseMessage] = [system_prompt, first_message]
        self.i = 0
        self.previous_state = None
		
    def step(self) -> tuple[ControllerPageState, AgentAction, ControllerActionResult]:
        self.i += 1

        state = self.controller.get_current_state(screenshot=self.use_vision)
        self._add_change_info(state, self.previous_state)
        self.previous_state = state

        action = self.get_next_action(state)

        if action.ask_human and action.ask_human.question:
            self._take_human_input(action.ask_human.question)
            action = self.get_next_action(state)

        result = self.controller.act(action)
        return state, action, result
    
    def _add_change_info(self, state: ControllerPageState, previous_state: ControllerPageState):
        if previous_state is not None:
            current_items = state.items
            previous_items_text = set(i.text for i in previous_state.items)
            for item in current_items:
                if item.text not in previous_items_text:
                    item.addition = True
    
    def _take_human_input(self, question: str) -> AgentAction:
        human_input = input(f'Human input required: {question}')
        self.messages.append(HumanMessage(content=human_input))
    
    def get_next_action(self, state: ControllerPageState) -> AgentAction:
        new_message = AgentMessagePrompt(state).get_user_message()
        input_messages = self.messages + [new_message]

        response: AgentAction = self.llm.invoke(input_messages)
        response_msg = AIMessage(content=response.model_dump_json())
        store_conversation(input_messages + [response_msg], step=self.i)

        # history_new_message = AgentMessagePrompt(state).get_message_for_history()
        # self.messages.append(history_new_message)
        self.messages.append(response_msg)

        return response