"""
AutoTestHub - CLICK Action Handler

Finds a permitted page element using an explicit wait for clickability
and triggers a click interaction.
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from actions import resolve_locator


def execute_click(
    driver: webdriver.Chrome,
    locator_type: str,
    locator_value: str,
    timeout_seconds: float = 10.0
) -> str:
    """
    Waits for an element to become clickable and clicks it.

    Args:
        driver (webdriver.Chrome): Active WebDriver session.
        locator_type (str): Locator strategy ('id', 'name', 'css', 'xpath').
        locator_value (str): Value of the locator selector.
        timeout_seconds (float): Maximum seconds to wait for clickability.

    Returns:
        str: Confirmation message.

    Raises:
        ValueError: If locator parameters are invalid.
        TimeoutError: If the element is not found/clickable within the timeout.
        RuntimeError: If interaction with the element fails.
    """
    by_strategy, selector = resolve_locator(locator_type, locator_value)

    try:
        element = WebDriverWait(driver, timeout_seconds).until(
            EC.element_to_be_clickable((by_strategy, selector))
        )
        element.click()
        return f"Clicked element ({locator_type}='{locator_value}')"
    except TimeoutException:
        raise TimeoutError(
            f"Timed out after {timeout_seconds}s waiting for element ({locator_type}='{locator_value}') to become clickable"
        )
    except WebDriverException as err:
        error_msg = getattr(err, "msg", str(err))
        raise RuntimeError(
            f"Failed to click element ({locator_type}='{locator_value}'): {error_msg}"
        )
