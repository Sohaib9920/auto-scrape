import pytest

from src.actions.browser_actions import BrowserActions
from src.agent_interface.planing_agent import PlaningAgent
from src.driver.service import DriverService
from src.state_manager.state import StateManager
import time

from src.state_manager.utils import save_chat

@pytest.fixture
def setup():
    driver = DriverService().get_driver()
    state_manager = StateManager(driver)
    actions = BrowserActions(driver)
    yield driver, actions, state_manager
    driver.quit()


def test_kayak_flight_search(setup):
    driver, actions, state_manager = setup
    task = 'Go to directly to the url kayak.com find a flight from Zürich to Bali on 2025-04-25 with return on 2025-06-05 for 2 people.'
    print(task)
    default_actions = actions.get_default_actions()
    agent = PlaningAgent(task=task, default_actions=default_actions, model="gpt-4o")
    url_history = []

    max_steps = 30
    for i in range(max_steps):
        print(f'Step {i}')
        current_state = state_manager.get_current_state()
        url_history.append(current_state.current_url)
        text = f'Elements: {current_state.interactable_elements}, Url history: {url_history}'
        action = agent.chat(text)
        save_chat(agent.input_messages, i)
        done = actions.execute_action(action, current_state.selector_map)
        if done:
            print('Task completed')
            break
        time.sleep(1)
    else:
        assert False, 'Failed to complete flight search task in maximum steps'

