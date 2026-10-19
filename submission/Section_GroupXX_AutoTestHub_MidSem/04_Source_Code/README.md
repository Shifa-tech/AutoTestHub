# AutoTestHub — Web Automation and Testing Platform using Selenium

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/tests-16%20passed-success.svg)]()
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-blue.svg)]()
[![License](https://img.shields.io/badge/license-Academic%20Evaluation-orange.svg)]()

## 1. Project Overview

**AutoTestHub** is a modular web automation and testing platform that simplifies cross-browser regression testing. It allows QA engineers and developers to define declarative test scenarios in JSON format, execute them in real Google Chrome instances (headless or windowed), capture automated visual screenshots, verify DOM title assertions, and persist structured test results in MongoDB via REST APIs.

---

## 2. System Architecture

AutoTestHub operates on a decoupled multi-tier pipeline:
```
[Selenium Control Desk UI] ──(HTTP)──> [Express REST API Gateway]
                                                │
                                        (child_process IPC)
                                                ▼
                                    [Python Selenium Worker]
                                                │
                                    (Selenium 4 / Chrome)
                                                ▼
                                    [Target Web Application]
```

### Module Responsibilities:
- **Member 1 (Ishree)**: Presentation Tier — `selenium-project/frontend/` (Control Desk, live terminal streaming, simulation viewport).
- **Member 2 (Shifa Siddiqui)**: Backend API & Database — `backend/` (Express routes, MongoDB schemas, Mongoose models).
- **Member 3 (Shruti Gupta)**: Selenium Engine — `selenium-worker/` (Runner CLI, dynamic action dispatchers, explicit waits, test harnesses).
- **Member 4 (Shristi Neekhra)**: Execution Bridge — `backend/services/executionService.js` (child_process spawning, IPC stdin/stdout, pipeline integration).

---

## 3. Directory Structure

```text
04_Source_Code/
├── README.md                      # This documentation file
├── sample_data/                   # Sample test cases, .env template, and seed data
│   ├── .env.example
│   ├── mock_db_seed.json
│   └── sample_tests/
└── source_files/
    ├── backend/                   # Node.js & Express REST API Server
    │   ├── config/database.js
    │   ├── controllers/testController.js
    │   ├── models/Testcase.js
    │   ├── models/Testresult.js
    │   ├── routes/testRoute.js
    │   ├── services/executionService.js
    │   ├── server.js
    │   └── testExecution.js
    ├── selenium-worker/           # Python Selenium Automation Engine
    │   ├── actions/
    │   ├── validators/
    │   ├── tests/
    │   ├── runner.py
    │   ├── browser.py
    │   └── requirements.txt
    └── selenium-project/          # Selenium Control Desk UI & Flask Server
        ├── frontend/
        └── app.py
```

---

## 4. Prerequisites

1. **Node.js (v18+)** and `npm`
2. **Python (v3.10+)**
3. **Google Chrome** installed (Selenium 4's built-in **Selenium Manager** automatically resolves the matching ChromeDriver)
4. **MongoDB (v6.0+)** running locally (`mongodb://127.0.0.1:27017/autotesthub`)

---

## 5. Build and Execution Instructions

### A. Running the Automation Engine Tests (Python Worker)
```bash
cd source_files/selenium-worker

# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run in-memory unit tests (fast, no browser launch)
python3 -m unittest tests/test_validation.py

# 4. Run end-to-end integration tests (launches Chrome sandbox)
python3 -m unittest discover tests

# 5. Execute a sample JSON test case directly
python3 runner.py sample_tests/form_interaction_test.json
```

### B. Running the Backend REST API Server
```bash
cd source_files/backend

# 1. Install dependencies
npm install

# 2. Configure environment
cp ../../sample_data/.env.example .env

# 3. Run standalone integration pipeline test
node testExecution.js

# 4. Start the backend REST server
node server.js
# API runs on http://localhost:5000
```

### C. Running the Selenium Control Desk UI
```bash
cd source_files/selenium-project

# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the interactive Control Desk
python3 app.py
# Open http://localhost:5000 in your browser
```

---

## 6. REST API Reference

| Method | Endpoint | Description | Sample Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status check | `200 OK` |
| `GET` | `/api/tests` | Retrieve all registered test definitions | `200 OK` |
| `POST` | `/api/tests` | Create a new test case document | `201 Created` |
| `POST` | `/api/tests/:id/run` | Execute the test via the Python engine | `200 OK` |

---

## 7. Academic Integrity & Project Contributors

- **Shristi Neekhra**: Execution Service, Integration Pipeline, Process Spawner, Mid-Semester Packaging.
- **Shifa Siddiqui**: Backend API Gateway, Express Routing, MongoDB Database Architecture.
- **Shruti Gupta**: Selenium Automation Engine, Chrome Lifecycle, Dynamic Actions, Test Suites.
- **Ishree**: Frontend Control Desk, Simulation Visualizer, Responsive Component Styling.
