"""
AutoTestHub - Browser Lifecycle Manager

Responsible for initializing, configuring, and safely terminating
the Selenium Chrome WebDriver instance.
"""

import os
import re
import sys
import uuid
from datetime import datetime
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_browser(headless: bool = True) -> webdriver.Chrome:
    """
    Initializes and returns a configured Chrome WebDriver instance.

    Uses Selenium 4's built-in Selenium Manager to automatically download
    and cache the matching ChromeDriver for the installed version of Google Chrome.

    Args:
        headless (bool): If True, runs Chrome in headless mode (without opening a GUI window).
                         Defaults to True for background/server execution.

    Returns:
        webdriver.Chrome: A ready-to-use Selenium WebDriver instance.
    """
    options = Options()

    if headless:
        # Modern headless mode introduced in Chrome 109+
        options.add_argument("--headless=new")

    # Standard stability options for automated environments
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Create and return the Chrome WebDriver
    driver = webdriver.Chrome(options=options)
    return driver


def close_browser(driver: Optional[webdriver.Chrome]) -> None:
    """
    Safely terminates a Chrome WebDriver session and cleans up resources.

    Guarantees that no lingering ChromeDriver or Chrome browser processes
    remain running, even if the browser has already crashed or an error occurred.

    Args:
        driver (Optional[webdriver.Chrome]): The active WebDriver instance to quit.
                                              If None, this function safely does nothing.
    """
    if driver is None:
        return

    try:
        driver.quit()
    except Exception as exc:
        # Diagnostic messages go to stderr so stdout remains clean for machine-readable JSON
        sys.stderr.write(f"[browser] Warning: Failed to cleanly quit driver: {exc}\n")


def capture_screenshot(
    driver: Optional[webdriver.Chrome],
    test_case_id: str,
    output_dir: str = "screenshots"
) -> Optional[str]:
    """
    Captures a full-window screenshot of the current browser state if an active
    session exists.

    Generates a unique, sanitized filename to prevent file collisions.
    Stores the image in a controlled output directory.

    Args:
        driver (Optional[webdriver.Chrome]): Active WebDriver session.
        test_case_id (str): Identifier for the test case.
        output_dir (str): Relative or absolute directory path to save screenshots.

    Returns:
        Optional[str]: Relative path to the saved screenshot file, or None if driver is inactive/failed.
    """
    if driver is None:
        return None

    try:
        # Ensure the controlled output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Sanitize test_case_id for use in filenames
        safe_id = re.sub(r"[^\w\-]", "_", test_case_id.strip()) if test_case_id else "test"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_token = uuid.uuid4().hex[:6]
        filename = f"{safe_id}_{timestamp}_{unique_token}.png"

        filepath = os.path.join(output_dir, filename)

        success = driver.save_screenshot(filepath)
        if success:
            # Normalize to forward slashes for cross-platform JSON response consistency
            normalized_path = filepath.replace("\\", "/")
            sys.stderr.write(f"[browser] Screenshot captured: {normalized_path}\n")
            return normalized_path
        else:
            sys.stderr.write(f"[browser] Warning: driver.save_screenshot returned False for {filepath}\n")
            return None

    except Exception as exc:
        # Never let screenshot failures break or mask test execution
        sys.stderr.write(f"[browser] Warning: Failed to capture screenshot: {exc}\n")
        return None


if __name__ == "__main__":
    print("Testing browser lifecycle management...")

    browser = None
    try:
        # Test 1: Initialize browser in headless mode
        print("1. Launching Chrome (headless mode)...")
        browser = create_browser(headless=True)
        print("   Chrome started successfully!")

        # Test 2: Perform a basic operation
        print("2. Opening test page...")
        browser.get("https://www.google.com")
        print(f"   Page Title: '{browser.title}'")

    except Exception as err:
        print(f"   An error occurred during test: {err}", file=sys.stderr)

    finally:
        # Test 3: Safe cleanup
        print("3. Closing browser session safely...")
        close_browser(browser)
        print("   Browser closed successfully!")
