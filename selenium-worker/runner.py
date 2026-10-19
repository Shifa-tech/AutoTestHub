"""
AutoTestHub - Structured Test Runner

Accepts a structured JSON test definition, validates input, executes supported
browser actions in sequence, guarantees resource cleanup, and outputs a single
machine-readable JSON execution result.
"""

import sys
import json
import time
from typing import Dict, Any, Tuple, Optional
from browser import create_browser, close_browser, capture_screenshot
from actions.open_url import execute_open_url
from actions.type_text import execute_type
from actions.click import execute_click
from validators.result_validator import assert_title

# Strict allowlist of supported actions to prevent arbitrary execution
SUPPORTED_ACTIONS = {"OPEN_URL", "ASSERT_TITLE", "TYPE", "CLICK"}


def validate_test_definition(data: Any) -> Tuple[bool, str]:
    """
    Performs comprehensive pre-flight validation on the input test definition.
    Catches structural flaws, unsupported actions, and missing parameters early.

    Args:
        data (Any): Parsed JSON data.

    Returns:
        Tuple[bool, str]: (is_valid, validation_error_message)
    """
    if not isinstance(data, dict):
        return False, "Test definition must be a JSON object"

    test_case_id = data.get("testCaseId")
    if not test_case_id or not isinstance(test_case_id, str) or not test_case_id.strip():
        return False, "Missing or invalid 'testCaseId' (must be a non-empty string)"

    actions = data.get("actions")
    if actions is None or not isinstance(actions, list):
        return False, "Missing or invalid 'actions' (must be a list)"

    for idx, action in enumerate(actions):
        if not isinstance(action, dict):
            return False, f"Action at index {idx} must be a JSON object"

        action_type = action.get("type")
        if not action_type or not isinstance(action_type, str):
            return False, f"Action at index {idx} is missing a valid 'type'"

        norm_type = action_type.strip().upper()
        if norm_type not in SUPPORTED_ACTIONS:
            return False, (
                f"Action at index {idx} has unsupported type '{action_type}'. "
                f"Supported actions: {sorted(list(SUPPORTED_ACTIONS))}"
            )

        if norm_type == "OPEN_URL":
            url = action.get("url") or data.get("url")
            if not url or not isinstance(url, str):
                return False, f"OPEN_URL action at index {idx} requires a 'url' string parameter"

        elif norm_type == "ASSERT_TITLE":
            if "expected" not in action or not isinstance(action.get("expected"), str):
                return False, f"ASSERT_TITLE action at index {idx} requires an 'expected' string parameter"

        elif norm_type in ("TYPE", "CLICK"):
            loc_type = action.get("locatorType") or action.get("by")
            loc_val = action.get("locator") or action.get("target") or action.get("selector")
            if not loc_type or not isinstance(loc_type, str):
                return False, f"{norm_type} action at index {idx} requires a 'locatorType' (e.g., 'id', 'name', 'css', 'xpath')"
            if not loc_val or not isinstance(loc_val, str) or not loc_val.strip():
                return False, f"{norm_type} action at index {idx} requires a non-empty 'locator' selector"
            if norm_type == "TYPE":
                val = action.get("value") if "value" in action else action.get("text")
                if val is None or not isinstance(val, str):
                    return False, f"TYPE action at index {idx} requires a 'value' or 'text' string parameter"

    return True, ""


def execute_action(driver, action: Dict[str, Any], test_def: Dict[str, Any]) -> Optional[str]:
    """
    Dispatches a single action to its handler.

    Args:
        driver: Active Selenium WebDriver instance.
        action (Dict[str, Any]): The action definition.
        test_def (Dict[str, Any]): The top-level test definition.

    Returns:
        Optional[str]: An optional status or result message from the action.
    """
    action_type = action["type"]

    if action_type not in SUPPORTED_ACTIONS:
        raise ValueError(f"Unsupported action type: '{action_type}'")

    if action_type == "OPEN_URL":
        # Check action parameter first, then fallback to test definition URL
        url = action.get("url") or test_def.get("url")
        if not url:
            raise ValueError("OPEN_URL action requires a 'url' parameter either in the action or top-level test definition")
        timeout = float(action.get("timeout", 30.0))
        execute_open_url(driver, url, timeout_seconds=timeout)
        return None

    elif action_type == "ASSERT_TITLE":
        expected = action.get("expected")
        if expected is None:
            raise ValueError("ASSERT_TITLE action requires an 'expected' string parameter")
        return assert_title(driver, expected)

    elif action_type == "TYPE":
        locator_type = action.get("locatorType") or action.get("by")
        locator_value = action.get("locator") or action.get("target") or action.get("selector")
        text = action.get("value") if "value" in action else action.get("text")
        timeout = float(action.get("timeout", 10.0))
        return execute_type(driver, locator_type, locator_value, text, timeout_seconds=timeout)

    elif action_type == "CLICK":
        locator_type = action.get("locatorType") or action.get("by")
        locator_value = action.get("locator") or action.get("target") or action.get("selector")
        timeout = float(action.get("timeout", 10.0))
        return execute_click(driver, locator_type, locator_value, timeout_seconds=timeout)

    return None


def execute_test(test_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the validated test definition using Selenium WebDriver.
    Measures execution time and guarantees browser cleanup.

    Args:
        test_def (Dict[str, Any]): Validated test definition.

    Returns:
        Dict[str, Any]: Structured execution result.
    """
    test_case_id = test_def.get("testCaseId", "unknown")
    actions = test_def.get("actions", [])
    start_time = time.perf_counter()

    driver = None
    # Step 1: Initialize browser in headless mode
    try:
        sys.stderr.write(f"[runner] Starting browser for testCaseId: '{test_case_id}'\n")
        driver = create_browser(headless=True)
    except Exception as startup_err:
        elapsed_time = round(time.perf_counter() - start_time, 2)
        sys.stderr.write(f"[runner] Browser startup failed: {startup_err}\n")
        return {
            "testCaseId": test_case_id,
            "status": "FAILED",
            "executionTime": elapsed_time,
            "screenshot": None,
            "message": "Browser startup failure",
            "errorMessage": str(startup_err)
        }

    try:
        # Step 2: Sequentially execute actions
        last_message = f"All {len(actions)} action(s) executed successfully"
        for idx, action in enumerate(actions):
            action_type = action.get("type")
            sys.stderr.write(f"[runner] Executing action {idx + 1}/{len(actions)}: {action_type}\n")
            action_result = execute_action(driver, action, test_def)
            if action_result:
                last_message = action_result

        elapsed_time = round(time.perf_counter() - start_time, 2)
        screenshot_path = capture_screenshot(driver, test_case_id)
        return {
            "testCaseId": test_case_id,
            "status": "PASSED",
            "executionTime": elapsed_time,
            "screenshot": screenshot_path,
            "message": last_message,
            "errorMessage": None
        }

    except AssertionError as assert_err:
        elapsed_time = round(time.perf_counter() - start_time, 2)
        screenshot_path = capture_screenshot(driver, test_case_id)
        sys.stderr.write(f"[runner] Assertion failed: {assert_err}\n")
        return {
            "testCaseId": test_case_id,
            "status": "FAILED",
            "executionTime": elapsed_time,
            "screenshot": screenshot_path,
            "message": "Assertion failed",
            "errorMessage": str(assert_err)
        }

    except TimeoutError as timeout_err:
        elapsed_time = round(time.perf_counter() - start_time, 2)
        screenshot_path = capture_screenshot(driver, test_case_id)
        sys.stderr.write(f"[runner] Action timeout: {timeout_err}\n")
        return {
            "testCaseId": test_case_id,
            "status": "FAILED",
            "executionTime": elapsed_time,
            "screenshot": screenshot_path,
            "message": "Execution timeout",
            "errorMessage": str(timeout_err)
        }

    except Exception as exc:
        elapsed_time = round(time.perf_counter() - start_time, 2)
        screenshot_path = capture_screenshot(driver, test_case_id)
        sys.stderr.write(f"[runner] Test failed: {exc}\n")
        return {
            "testCaseId": test_case_id,
            "status": "FAILED",
            "executionTime": elapsed_time,
            "screenshot": screenshot_path,
            "message": "Test execution encountered a failure",
            "errorMessage": str(exc)
        }

    finally:
        # Step 3: Guaranteed browser cleanup
        sys.stderr.write("[runner] Closing browser session...\n")
        close_browser(driver)


def parse_input() -> Dict[str, Any]:
    """
    Reads and parses JSON input either from a file path specified as a CLI argument,
    or from standard input (stdin).

    Returns:
        Dict[str, Any]: Parsed JSON test definition.
    """
    raw_content = ""
    if len(sys.argv) > 1:
        # Input provided via file path argument
        file_path = sys.argv[1]
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    else:
        # Input provided via stdin (e.g. piped from Node.js)
        raw_content = sys.stdin.read()

    if not raw_content.strip():
        raise ValueError("No input provided (expected JSON test definition from file or stdin)")

    return json.loads(raw_content)


def main() -> int:
    """
    Main entry point for runner.py.
    Always outputs exactly one JSON result to stdout.
    Returns 0 for PASSED, 1 for FAILED.
    """
    try:
        test_def = parse_input()
    except Exception as parse_err:
        result = {
            "testCaseId": "unknown",
            "status": "FAILED",
            "executionTime": 0.0,
            "screenshot": None,
            "message": "Failed to parse test definition input",
            "errorMessage": str(parse_err)
        }
        print(json.dumps(result, indent=2))
        return 1

    # Validate structure
    is_valid, validation_msg = validate_test_definition(test_def)
    if not is_valid:
        result = {
            "testCaseId": test_def.get("testCaseId", "unknown") if isinstance(test_def, dict) else "unknown",
            "status": "FAILED",
            "executionTime": 0.0,
            "screenshot": None,
            "message": "Input validation failed",
            "errorMessage": validation_msg
        }
        print(json.dumps(result, indent=2))
        return 1

    # Execute test
    result = execute_test(test_def)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
