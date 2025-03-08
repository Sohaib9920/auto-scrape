import unittest
from src.utils.selenium_utils import setup_selenium_driver


class TestSeleniumUtils(unittest.TestCase):
    def test_setup_selenium_driver(self):
        driver = setup_selenium_driver(headless=True)
        self.assertIsNotNone(driver)
        driver.quit()
        