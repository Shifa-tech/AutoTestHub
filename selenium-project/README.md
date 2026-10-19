# Selenium Control Desk (frontend + real Chrome backend)

## Requirements
- Python 3.9 or newer
- Google Chrome installed

## Steps
1. Open a terminal in this folder.
2. Create and activate a virtual environment:
       python3 -m venv venv
       source venv/bin/activate        # Windows: venv\Scripts\activate
3. Install dependencies:
       pip install -r requirements.txt
4. Start the server:
       python app.py
5. Open http://localhost:5000 in your browser.
6. Pick a task, fill its inputs, press "Run task". A real Chrome window opens.

If you open frontend/index.html directly instead, the page runs in simulation mode.

## Files
- app.py: Flask server. Runs the four Selenium tasks and serves the frontend.
- frontend/: index.html, css/style.css, js/app.js
- form_submissions.txt and form_result.png are created when you run tasks.

## Notes
- Selenium 4.6+ downloads ChromeDriver by itself, so webdriver-manager is not needed.
- Google may show a captcha for automated searches. Solve it in the window if it appears.
- Only one task runs at a time. Use Stop to end a run.
