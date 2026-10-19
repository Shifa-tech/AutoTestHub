"""
AutoTestHub - OPEN_URL Action Handler

Validates target URLs (enforcing HTTP/HTTPS schemes) and instructs
the browser to navigate to the specified page.
"""

from urllib.parse import urlparse
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException


ALLOWED_SCHEMES = {"http", "https"}


def validate_url(url: str) -> str:
    """
    Validates that a URL is safe and well-formed.

    Rules:
    - Must be a non-empty string.
    - Only 'http' and 'https' schemes are permitted.
    - Local file URLs (file://), javascript: execution, or data: URIs are strictly rejected.
    - Must contain a valid network location (host).

    Args:
        url (str): The raw URL to validate.

    Returns:
        str: The trimmed, valid URL.

    Raises:
        ValueError: If the URL is missing, malformed, or uses an unsupported scheme.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string")

    cleaned_url = url.strip()
    try:
        parsed = urlparse(cleaned_url)
    except Exception as exc:
        raise ValueError(f"Malformed URL '{cleaned_url}': {exc}")

    if not parsed.scheme:
        raise ValueError(f"URL '{cleaned_url}' is missing a scheme (e.g., 'https://')")

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValueError(
            f"Unsupported URL scheme '{parsed.scheme}'. Only {ALLOWED_SCHEMES} are permitted."
        )

    if not parsed.netloc:
        raise ValueError(f"URL '{cleaned_url}' is missing a valid host or domain")

    return cleaned_url


def execute_open_url(driver: webdriver.Chrome, url: str, timeout_seconds: float = 30.0) -> None:
    """
    Navigates the browser to the specified URL after validation.

    Args:
        driver (webdriver.Chrome): Active WebDriver session.
        url (str): Target URL to navigate to.
        timeout_seconds (float): Maximum seconds to wait for page load (default: 30.0).

    Raises:
        ValueError: If the URL fails validation.
        TimeoutError: If page loading times out.
        RuntimeError: If Selenium fails to navigate to the page.
    """
    valid_url = validate_url(url)
    try:
        driver.set_page_load_timeout(timeout_seconds)
        driver.get(valid_url)
    except TimeoutException:
        raise TimeoutError(f"Navigation timed out after {timeout_seconds}s loading '{valid_url}'")
    except WebDriverException as err:
        error_msg = getattr(err, "msg", str(err))
        raise RuntimeError(f"Failed to navigate to '{valid_url}': {error_msg}")
