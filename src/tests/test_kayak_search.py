import pytest
import os
from src.actions.browser_actions import ActionResult, BrowserActions
from src.agent_interface.planing_agent import PlaningAgent
from src.driver.service import DriverService
from src.state_manager.state import StateManager
import time
from datetime import datetime
from src.state_manager.utils import save_formatted_html


@pytest.fixture
def setup():
    driver = DriverService().get_driver()
    state_manager = StateManager(driver)
    actions = BrowserActions(driver)
    yield driver, actions, state_manager
    driver.quit()


def test_kayak_flight_search(setup):
    driver, actions, state_manager = setup

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_folder = f'temp/run_{timestamp}'
    if not os.path.exists(run_folder):
        os.makedirs(run_folder)
           
    task = 'Go to kayak.com and find a flight from Zürich to (ask the user for the destination) on 2025-04-25 with return on 2025-06-05 for 2 people.'

    default_actions = actions.get_default_actions()
    print(default_actions)
    agent = PlaningAgent(default_actions=default_actions, model="gpt-4o")
    agent.add_user_prompt(f'Your task is: {task}', after_system=True)

    url_history = []
    previous_state = None
    output = ActionResult()
    max_steps = 30

    for i in range(max_steps):
        print(f'Step {i}')
        current_state = state_manager.get_current_state(run_folder=run_folder, step=i)

        save_formatted_html(driver.page_source, f'{run_folder}/html_{i}.html')
        url_history.append(current_state.current_url)

        state_manager.add_change_info(current_state=current_state, previous_state=previous_state)
        state_manager.add_parent_info(current_state=current_state)
        elem_text = "\n".join([e.get_text() for e in current_state.interactable_elements])

        text = f'Elements:\n{elem_text}\nUrl history: {url_history}'

        if output.user_input:
            agent.add_user_prompt(output.user_input)
        if output.error:
            text += f'\nPrevious action error: {output.error}'

        action = agent.chat(
            text, 
            store_conversation=f'{run_folder}/conversation_{i}.txt',
            image=current_state.screenshot
        )

        input("Press Enter to continue...")

        output = actions.execute_action(action, current_state.selector_map)

        if output.done:
            print('Task completed')
            break

        previous_state = current_state
        time.sleep(1)
        
    else:
        assert False, 'Failed to complete flight search task in maximum steps'

