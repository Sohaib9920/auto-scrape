from src.agent.service import AgentService
from src.controller.service import ControllerService
from langchain_openai import ChatOpenAI

task = input("Enter task: ")
# task = 'Go to kayak.com and find cheapest flight from Karachi to Jeddah on 2025-05-25 with return on 2025-06-05 for 2 people.'

model = ChatOpenAI(model='gpt-4o')
controller = ControllerService()
agent = AgentService(task, model, controller, use_vision=True)

try:
    max_steps = 30
    for i in range(max_steps):
        print(f'\n📍 Step {i+1}')
        state, action, result = agent.step()
        if result.done:
            print('\n✅ Task completed successfully')
            break
        # input("continue?")
    else:
        print('\n' + '=' * 50)
        print('❌ Failed to complete task in maximum steps')
        print('=' * 50)
        assert False, 'Failed to complete task in maximum steps'

except KeyboardInterrupt:
    print('\n\nReceived interrupt, closing browser...')
    raise

finally:
	controller.browser.close()