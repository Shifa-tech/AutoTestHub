"""
Unit Tests for AutoTestHub Input Validation and Resolvers
Fast, in-memory tests that do not require browser launch.
"""

import unittest
from selenium.webdriver.common.by import By

from runner import validate_test_definition
from actions.open_url import validate_url
from actions import resolve_locator


class TestValidation(unittest.TestCase):

    def test_valid_test_definition(self):
        valid_def = {
            "testCaseId": "tc-001",
            "name": "Sample Test",
            "url": "https://example.com",
            "actions": [
                {"type": "OPEN_URL"},
                {"type": "ASSERT_TITLE", "expected": "Example Domain"}
            ]
        }
        is_valid, msg = validate_test_definition(valid_def)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

    def test_missing_test_case_id(self):
        invalid_def = {
            "actions": [{"type": "OPEN_URL", "url": "https://example.com"}]
        }
        is_valid, msg = validate_test_definition(invalid_def)
        self.assertFalse(is_valid)
        self.assertIn("testCaseId", msg)

    def test_missing_actions_list(self):
        invalid_def = {"testCaseId": "tc-002"}
        is_valid, msg = validate_test_definition(invalid_def)
        self.assertFalse(is_valid)
        self.assertIn("actions", msg)

    def test_unsupported_action(self):
        invalid_def = {
            "testCaseId": "tc-003",
            "actions": [{"type": "EXEC_SHELL_COMMAND"}]
        }
        is_valid, msg = validate_test_definition(invalid_def)
        self.assertFalse(is_valid)
        self.assertIn("unsupported type", msg)

    def test_valid_urls(self):
        self.assertEqual(validate_url("http://localhost:5000"), "http://localhost:5000")
        self.assertEqual(validate_url("https://example.com/test"), "https://example.com/test")

    def test_invalid_urls_rejected(self):
        # Local files, javascript, and data schemes must be rejected
        with self.assertRaises(ValueError):
            validate_url("file:///etc/passwd")

        with self.assertRaises(ValueError):
            validate_url("javascript:alert(1)")

        with self.assertRaises(ValueError):
            validate_url("data:text/html,<h1>test</h1>")

        with self.assertRaises(ValueError):
            validate_url("not-a-valid-url")

    def test_locator_resolution(self):
        by, sel = resolve_locator("id", "submit-btn")
        self.assertEqual(by, By.ID)
        self.assertEqual(sel, "submit-btn")

        by, sel = resolve_locator("css", ".btn-primary")
        self.assertEqual(by, By.CSS_SELECTOR)

        by, sel = resolve_locator("name", "username")
        self.assertEqual(by, By.NAME)

        by, sel = resolve_locator("xpath", "//button")
        self.assertEqual(by, By.XPATH)

    def test_unsupported_locator_rejected(self):
        with self.assertRaises(ValueError):
            resolve_locator("unsupported_strategy", "foo")


if __name__ == "__main__":
    unittest.main()
