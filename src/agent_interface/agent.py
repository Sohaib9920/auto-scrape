from typing import Dict, List

# agent
class Agent:
    def __init__(self):
        self.current_state = None
        self.available_actions = None
        self.task = None
        self.context = None
    
    def receive_state(self, state: Dict, actions: List):
        self.current_state = state
        self.available_actions = actions
    
    def decide_next_action(self) -> Dict:
        pass
