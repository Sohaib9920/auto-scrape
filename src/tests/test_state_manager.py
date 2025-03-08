import unittest
from src.state_manager.state import StateManager
from src.utils.selenium_utils import setup_selenium_driver


class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.driver = setup_selenium_driver(headless=True)
        self.state_manager = StateManager(self.driver)

    def tearDown(self):
        self.driver.quit()

    def test_get_current_state(self):
        test_url = "https://www.example.com/"
        self.driver.get(test_url)
        state = self.state_manager.get_current_state()
        self.assertEqual(state["current_url"], test_url)