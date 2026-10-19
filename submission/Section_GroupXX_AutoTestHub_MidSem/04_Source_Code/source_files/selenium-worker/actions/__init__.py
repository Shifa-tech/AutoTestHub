"""
AutoTestHub - Browser Actions Package

Contains individual modular actions and locator resolution helpers.
"""

from typing import Tuple
from selenium.webdriver.common.by import By

# Strict allowlist of supported locator strategies
SUPPORTED_LOCATORS = {
    "id": By.ID,
    "name": By.NAME,
    "css": By.CSS_SELECTOR,
    "xpath": By.XPATH,
}


def resolve_locator(locator_type: str, locator_value: str) -> Tuple[str, str]:
    """
    Validates and maps a locator strategy string to Selenium's By constant.

    Supported strategies: 'id', 'name', 'css', 'xpath'.

    Args:
        locator_type (str): The strategy name (case-insensitive).
        locator_value (str): The selector string.

    Returns:
        Tuple[str, str]: (Selenium By constant, cleaned selector value)

    Raises:
        ValueError: If the locator strategy or selector value is invalid.
    """
    if not locator_type or not isinstance(locator_type, str):
        raise ValueError("Missing or invalid locator type (expected 'id', 'name', 'css', or 'xpath')")

    norm_type = locator_type.strip().lower()
    if norm_type not in SUPPORTED_LOCATORS:
        raise ValueError(
            f"Unsupported locator strategy '{locator_type}'. "
            f"Allowed strategies: {sorted(list(SUPPORTED_LOCATORS.keys()))}"
        )

    if not locator_value or not isinstance(locator_value, str) or not locator_value.strip():
        raise ValueError("Locator value must be a non-empty string")

    return SUPPORTED_LOCATORS[norm_type], locator_value.strip()
