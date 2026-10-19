# AutoTestHub — Selenium Automation Engine (Worker Module)

This module is the core test execution engine for **AutoTestHub**, responsible for executing automated browser tests using Python and Selenium WebDriver.

## System Architecture Role

AutoTestHub works in a multi-service pipeline:
```
React Frontend → Node.js/Express Backend → Execution Service → Python Selenium Worker → Chrome Browser
```

- **Member 1**: React Frontend
- **Member 2**: Express APIs & MongoDB Models
- **Member 3 (This Module)**: Python Selenium Worker
- **Member 4**: Execution Service (invoking this worker)

---

## Directory Structure

```text
selenium-worker/
    runner.py                   # Main test runner CLI and input/output coordinator
    browser.py                  # Chrome WebDriver lifecycle management and screenshots
    actions/
        __init__.py             # Action package and locator resolution helpers
        open_url.py             # OPEN_URL action handler with URL safety validation
        type_text.py            # TYPE action handler with explicit waits
        click.py                # CLICK action handler with explicit waits
    validators/
        __init__.py             # Validator package
        result_validator.py     # ASSERT_TITLE assertion handler
    tests/
        __init__.py             # Test suite package
        test_validation.py      # Fast, in-memory unit tests (no browser needed)
        test_integration.py     # End-to-end integration tests using local HTTP server
    sample_tests/
        minimal_test.json       # Minimal test definition baseline
        open_url_test.json      # URL navigation test case
        assert_title_test.json  # Title assertion test case
        form_interaction_test.json # End-to-end form fill and submission test
    requirements.txt            # Minimal dependency definition (Selenium 4)
    .gitignore                  # Excludes venvs, bytecode, and runtime screenshots
    README.md                   # Engine documentation and guide
```

---

## Prerequisites (Windows)

1. **Python 3.10+** (Python 3.12 is installed and supported)
2. **Google Chrome** installed (Selenium 4's built-in **Selenium Manager** automatically manages the matching ChromeDriver)

---

## Setup Instructions (Windows)

### 1. Open Terminal and Navigate to Worker Directory
```powershell
cd "AutoTestHub\selenium-worker"
```

### 2. Create and Activate Virtual Environment

> **Note for OneDrive / Cloud Synced Folders:**
> When your project folder is located inside a OneDrive synced directory, creating virtual environments directly inside the synced folder can cause Windows DLL lock issues. The recommended standard on Windows is placing the virtual environment in your user profile folder:

```powershell
# Create isolated virtual environment
python -m venv "$env:USERPROFILE\.venvs\selenium-worker"

# Allow script execution for current PowerShell session (if restricted)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activate virtual environment
& "$env:USERPROFILE\.venvs\selenium-worker\Scripts\Activate.ps1"
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## Running Automated Tests

### Run Fast In-Memory Unit Tests
```powershell
python -m unittest tests/test_validation.py
```

### Run End-to-End Integration Tests (Uses local test sandbox)
```powershell
python -m unittest tests/test_integration.py
```

### Run All Tests
```powershell
python -m unittest discover tests
```

---

## Execution Interface (Contract with Member 4)

### Input Contract
The runner accepts JSON input either via a **file path argument** or piped via **standard input (stdin)**:

```powershell
# Via file argument
python runner.py sample_tests/form_interaction_test.json

# Via stdin pipe
cat sample_tests/form_interaction_test.json | python runner.py
```

#### Request Schema Example:
```json
{
  "testCaseId": "demo-001",
  "name": "Demo Web Form Test",
  "url": "https://www.selenium.dev/selenium/web/web-form.html",
  "actions": [
    {
      "type": "OPEN_URL"
    },
    {
      "type": "TYPE",
      "locatorType": "name",
      "locator": "my-text",
      "value": "Test User"
    },
    {
      "type": "CLICK",
      "locatorType": "css",
      "locator": "button"
    },
    {
      "type": "ASSERT_TITLE",
      "expected": "Web form - target page"
    }
  ]
}
```

### Output Contract
- **`stdout`**: Exactly ONE valid JSON string (safe for Node.js `JSON.parse()`).
- **`stderr`**: Diagnostic runtime logs.
- **Exit Code**: `0` for `PASSED`, `1` for `FAILED`.

#### Response Schema Example:
```json
{
  "testCaseId": "demo-001",
  "status": "PASSED",
  "executionTime": 2.14,
  "screenshot": "screenshots/demo-001_20261018_163043_171dec.png",
  "message": "Page title matched 'Web form - target page'",
  "errorMessage": null
}
```

---

## Supported Browser Actions

| Action | Required Fields | Optional Fields | Description |
| :--- | :--- | :--- | :--- |
| `OPEN_URL` | `url` (in action or root) | `timeout` (default: 30.0s) | Safely navigates to an HTTP/HTTPS URL. Rejects file/javascript schemes. |
| `TYPE` | `locatorType`, `locator`, `value` | `timeout` (default: 10.0s) | Waits for element visibility, clears text, and enters input. |
| `CLICK` | `locatorType`, `locator` | `timeout` (default: 10.0s) | Waits for element clickability and clicks it. |
| `ASSERT_TITLE` | `expected` | `timeout` (default: 5.0s) | Explicitly waits for title match; raises assertion failure on mismatch. |

**Allowed Locator Strategies:** `id`, `name`, `css`, `xpath`.
