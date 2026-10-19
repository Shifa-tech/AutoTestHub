"""
AutoTestHub - TYPE Action Handler

Finds a permitted page element using an explicit wait, clears it,
and inputs the specified text value.
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from actions import resolve_locator


def execute_type(
    driver: webdriver.Chrome,
    locator_type: str,
    locator_value: str,
    text: str,
    timeout_seconds: float = 10.0
) -> str:
    """
    Waits for an element to become visible, clears its current content,
    and types the specified text.

    Args:
        driver (webdriver.Chrome): Active WebDriver session.
        locator_type (str): Locator strategy ('id', 'name', 'css', 'xpath').
        locator_value (str): Value of the locator selector.
        text (str): Text string to type into the field.
        timeout_seconds (float): Maximum seconds to wait for visibility.

    Returns:
        str: Confirmation message.

    Raises:
        ValueError: If locator or text parameters are invalid.
        TimeoutError: If the element is not found/visible within the timeout.
        RuntimeError: If interaction with the element fails.
    """
    if text is None or not isinstance(text, str):
        raise ValueError("TYPE action requires a valid string for 'value' or 'text'")

    by_strategy, selector = resolve_locator(locator_type, locator_value)

    try:
        element = WebDriverWait(driver, timeout_seconds).until(
            EC.visibility_of_element_located((by_strategy, selector))
        )
        element.clear()
        element.send_keys(text)
        return f"Typed text into element ({locator_type}='{locator_value}')"
    except TimeoutException:
        raise TimeoutError(
            f"Timed out after {timeout_seconds}s waiting for element ({locator_type}='{locator_value}') to become visible"
        )
    except WebDriverException as err:
        error_msg = getattr(err, "msg", str(err))
        raise RuntimeError(
            f"Failed to type into element ({locator_type}='{locator_value}'): {error_msg}"
        )
