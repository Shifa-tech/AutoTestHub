"""Backend for the Selenium Control Desk: runs real Chrome via Selenium
and serves the frontend. Start with:  python app.py  ->  http://localhost:5000"""
import os, threading, uuid
from flask import Flask, jsonify, request, send_from_directory
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE, "frontend"), static_url_path="")
RUNS, LOCK = {}, threading.Lock()
SEL_FORM = "https://www.selenium.dev/selenium/web/web-form.html"
W3_FORM = "https://www.w3schools.com/html/tryit.asp?filename=tryhtml_form_submit"


class Stopped(Exception):
    pass


class Run:
    def __init__(self):
        self.id = uuid.uuid4().hex[:8]
        self.lines, self.state, self.progress = [], "running", 0
        self.result = self.error = ""
        self.file = None
        self.stop = threading.Event()

    def log(self, msg, cls=""):
        self.lines.append({"msg": msg, "cls": cls})

    def wait(self, sec):  # sleep that reacts to the Stop button
        if self.stop.wait(sec):
            raise Stopped()

    def check(self):
        if self.stop.is_set():
            raise Stopped()


def t_demo(r, d, p):
    url = (p.get("url") or "https://www.google.com").strip()
    if not url.startswith("http"):
        url = "https://" + url
    r.log(f'driver.get("{url}")')
    d.get(url)
    r.progress = 70
    r.log(f"Title of the page is: {d.title}", "ok")
    return f"Opened {url} · title “{d.title}”"


def t_search(r, d, p):
    q = (p.get("query") or "").strip()
    if not q:
        raise ValueError("Type a search term first.")
    r.log('driver.get("https://www.google.com")')
    d.get("https://www.google.com")
    box = WebDriverWait(d, 10).until(EC.presence_of_element_located((By.NAME, "q")))
    r.progress = 40
    r.log(f"Typing: {q}")
    box.send_keys(q)
    box.send_keys(Keys.RETURN)
    r.wait(3)
    r.progress = 80
    r.log(f"Page title after search: {d.title}", "ok")
    return f"Searched “{q}”"


def t_form(r, d, p):
    r.log(f'driver.get("{SEL_FORM}")')
    d.get(SEL_FORM)
    r.wait(2)
    d.find_element(By.NAME, "my-text").send_keys(p.get("text", ""))
    d.find_element(By.NAME, "my-password").send_keys(p.get("pass", ""))
    r.progress = 60
    r.log("Filled text and password fields")
    d.find_element(By.CSS_SELECTOR, "button").click()
    r.wait(2)
    d.save_screenshot(os.path.join(BASE, "form_result.png"))
    r.log("Saved screenshot: form_result.png", "ok")
    r.log(f"Page title: {d.title}", "ok")
    return "Form submitted · screenshot saved"


def t_auto(r, d, p):
    people = p.get("people") or []
    if not people:
        raise ValueError("Add at least one person first.")
    path = os.path.join(BASE, "form_submissions.txt")
    text = "Form Submission Report\n=======================\n\n"
    with open(path, "w") as f:
        f.write(text)
    r.file = text
    for i, (first, last) in enumerate(people, 1):
        r.check()
        d.get(W3_FORM)
        WebDriverWait(d, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "iframeResult")))
        a, b = d.find_element(By.ID, "fname"), d.find_element(By.ID, "lname")
        a.clear(); b.clear()
        a.send_keys(first); b.send_keys(last)
        d.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        line = f"Form submitted for: {first} {last}"
        r.log(line, "ok")
        text += line + "\n"
        with open(path, "a") as f:
            f.write(line + "\n")
        r.file = text
        r.progress = 15 + int(85 * i / len(people))
        r.wait(2)
    r.log("All submissions saved in: form_submissions.txt", "ok")
    return f"Submitted {len(people)} form(s)"


TASKS = {"demo": t_demo, "search": t_search, "form": t_form, "auto": t_auto}


def worker(r, task, headless, params):
    d, state = None, "done"
    try:
        r.log("Launching Chrome (Selenium Manager fetches the driver) …")
        o = webdriver.ChromeOptions()
        if headless:
            o.add_argument("--headless=new")
        d = webdriver.Chrome(options=o)
        if not headless:
            d.maximize_window()
        r.log("Chrome launched", "ok")
        r.progress = 15
        r.result = TASKS[task](r, d, params)
        r.progress = 100
    except Stopped:
        state = "stopped"
    except Exception as e:
        state = "error"
        r.error = (str(e).strip().splitlines() or [type(e).__name__])[0]
    finally:
        if d:
            try:
                d.quit()
            except Exception:
                pass
            r.log("Browser closed", "ok")
        r.state = state


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    return jsonify(ok=True)


@app.post("/api/run")
def run():
    data = request.get_json(force=True)
    task = data.get("task")
    if task not in TASKS:
        return jsonify(error="Unknown task"), 400
    with LOCK:
        if any(x.state == "running" for x in RUNS.values()):
            return jsonify(error="A task is already running. Stop it first."), 409
        r = Run()
        RUNS[r.id] = r
    threading.Thread(target=worker, daemon=True,
                     args=(r, task, bool(data.get("headless")), data.get("params", {}))).start()
    return jsonify(id=r.id)


@app.get("/api/events/<rid>")
def events(rid):
    r = RUNS.get(rid)
    if not r:
        return jsonify(error="Unknown run"), 404
    since = int(request.args.get("since", 0))
    return jsonify(lines=r.lines[since:], next=len(r.lines), state=r.state,
                   progress=r.progress, result=r.result, error=r.error, file=r.file)


@app.post("/api/stop/<rid>")
def stop(rid):
    r = RUNS.get(rid)
    if r:
        r.stop.set()
    return jsonify(ok=True)


if __name__ == "__main__":
    print("Open http://localhost:5000 in your browser")
    app.run(host="127.0.0.1", port=5000, threaded=True)
