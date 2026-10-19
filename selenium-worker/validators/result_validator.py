"""
AutoTestHub - Result Validator

Contains assertions to verify expected browser states, such as page title.
"""

from typing import Optional
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def assert_title(driver: webdriver.Chrome, expected: str, timeout_seconds: float = 5.0) -> str:
    """
    Asserts that the browser's page title matches the expected title.
    Uses an explicit wait to allow pending navigations or asynchronous title updates to complete.

    Args:
        driver (webdriver.Chrome): The active WebDriver session.
        expected (str): The expected page title string.
        timeout_seconds (float): Maximum seconds to wait for title match (default: 5.0).

    Returns:
        str: A success message indicating that the title matched.

    Raises:
        ValueError: If 'expected' is missing or not a string.
        AssertionError: If the actual browser title does not match the expected title.
    """
    if expected is None or not isinstance(expected, str):
        raise ValueError("ASSERT_TITLE action requires a valid string for 'expected'")

    try:
        WebDriverWait(driver, timeout_seconds).until(EC.title_is(expected))
    except TimeoutException:
        actual = driver.title
        raise AssertionError(
            f"Page title mismatch: expected '{expected}', but got '{actual}'"
        )

    return f"Page title matched '{expected}'"
