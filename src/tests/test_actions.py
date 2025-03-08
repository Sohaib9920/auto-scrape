import unittest
from src.actions.browser_actions import BrowserActions
from src.utils.selenium_utils import setup_selenium_driver


class TestBrowserActions(unittest.TestCase):
    def setUp(self):
        self.driver = setup_selenium_driver(headless=True)
        self.actions = BrowserActions(self.driver)
    
    def tearDown(self):
        self.driver.quit()
    
    def test_go_to_url(self):
        test_url = "https://www.example.com/"
        self.actions.go_to_url(test_url)
        self.assertEqual(self.driver.current_url, test_url)