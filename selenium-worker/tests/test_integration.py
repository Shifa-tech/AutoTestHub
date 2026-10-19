"""
Integration Tests for AutoTestHub Runner and Actions
Uses a controlled local HTTP server to verify end-to-end browser execution,
screenshot capture, assertion verification, and cleanup after failures.
"""

import os
import shutil
import threading
import unittest
from http.server import HTTPServer, BaseHTTPRequestHandler

from runner import execute_test


HTML_CONTENT = """<!DOCTYPE html>
<html>
<head><title>Controlled Test Sandbox</title></head>
<body>
  <h1>AutoTestHub Test Server</h1>
  <input id="test-input" name="search_query" type="text" />
  <button id="test-button" onclick="document.title='Action Completed'">Submit</button>
</body>
</html>"""


class ControlledHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode("utf-8"))

    def log_message(self, format, *args):
        # Silence local server request logs to keep test output clean
        pass


class TestRunnerIntegration(unittest.TestCase):
    server = None
    server_thread = None
    base_url = None

    @classmethod
    def setUpClass(cls):
        # Start a local HTTP server on a dynamically assigned port
        cls.server = HTTPServer(("127.0.0.1", 0), ControlledHandler)
        cls.port = cls.server.server_port
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        if cls.server:
            cls.server.shutdown()
            cls.server.server_close()
        # Clean up any test screenshots produced during integration tests
        if os.path.exists("screenshots"):
            shutil.rmtree("screenshots", ignore_errors=True)

    def test_valid_url_navigation(self):
        test_def = {
            "testCaseId": "int-nav-01",
            "url": self.base_url,
            "actions": [{"type": "OPEN_URL"}]
        }
        result = execute_test(test_def)
        self.assertEqual(result["status"], "PASSED")
        self.assertIsNone(result["errorMessage"])

    def test_matching_title_assertion(self):
        test_def = {
            "testCaseId": "int-title-pass",
            "url": self.base_url,
            "actions": [
                {"type": "OPEN_URL"},
                {"type": "ASSERT_TITLE", "expected": "Controlled Test Sandbox"}
            ]
        }
        result = execute_test(test_def)
        self.assertEqual(result["status"], "PASSED")
        self.assertIn("Controlled Test Sandbox", result["message"])

    def test_mismatched_title_assertion(self):
        test_def = {
            "testCaseId": "int-title-fail",
            "url": self.base_url,
            "actions": [
                {"type": "OPEN_URL"},
                {"type": "ASSERT_TITLE", "expected": "Incorrect Title Expectation"}
            ]
        }
        result = execute_test(test_def)
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["message"], "Assertion failed")
        self.assertIn("Page title mismatch", result["errorMessage"])

    def test_type_and_click_interaction(self):
        test_def = {
            "testCaseId": "int-form-flow",
            "url": self.base_url,
            "actions": [
                {"type": "OPEN_URL"},
                {"type": "TYPE", "locatorType": "id", "locator": "test-input", "value": "Test automation"},
                {"type": "CLICK", "locatorType": "id", "locator": "test-button"},
                {"type": "ASSERT_TITLE", "expected": "Action Completed"}
            ]
        }
        result = execute_test(test_def)
        self.assertEqual(result["status"], "PASSED")

    def test_missing_element_timeout(self):
        test_def = {
            "testCaseId": "int-timeout",
            "url": self.base_url,
            "actions": [
                {"type": "OPEN_URL"},
                {"type": "CLICK", "locatorType": "id", "locator": "nonexistent-button", "timeout": 1.0}
            ]
        }
        result = execute_test(test_def)
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["message"], "Execution timeout")
        self.assertIn("Timed out", result["errorMessage"])

    def test_screenshot_created_on_success(self):
        test_def = {
            "testCaseId": "int-screen-pass",
            "url": self.base_url,
            "actions": [{"type": "OPEN_URL"}]
        }
        result = execute_test(test_def)
        self.assertEqual(result["status"], "PASSED")
        self.assertIsNotNone(result["screenshot"])
        self.assertTrue(os.path.exists(result["screenshot"]))

    def test_screenshot_created_on_failure(self):
        test_def = {
            "testCaseId": "int-screen-fail",
            "url": self.base_url,
            "actions": [
                {"type": "OPEN_URL"},
                {"type": "ASSERT_TITLE", "expected": "Wrong Title"}
            ]
        }
        result = execute_test(test_def)
        self.assertEqual(result["status"], "FAILED")
        self.assertIsNotNone(result["screenshot"])
        self.assertTrue(os.path.exists(result["screenshot"]))

    def test_cleanup_after_failure(self):
        # Verify that subsequent tests run cleanly even after an action failure
        test_def_fail = {
            "testCaseId": "int-fail-cleanup",
            "url": self.base_url,
            "actions": [
                {"type": "OPEN_URL"},
                {"type": "CLICK", "locatorType": "id", "locator": "missing-elem", "timeout": 0.5}
            ]
        }
        res_fail = execute_test(test_def_fail)
        self.assertEqual(res_fail["status"], "FAILED")

        # Run another test immediately to ensure browser resources were freed and new session succeeds
        test_def_next = {
            "testCaseId": "int-after-fail",
            "url": self.base_url,
            "actions": [{"type": "OPEN_URL"}]
        }
        res_next = execute_test(test_def_next)
        self.assertEqual(res_next["status"], "PASSED")


if __name__ == "__main__":
    unittest.main()
