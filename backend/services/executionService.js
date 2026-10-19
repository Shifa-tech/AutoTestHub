
const { spawn } = require("child_process");
const path = require("path");

const workerPath = path.resolve(
  __dirname,
  "../../selenium-worker/runner.py"
);

const pythonCommand = process.env.PYTHON_EXECUTABLE || "python";

function runSeleniumTest(testCase) {
  return new Promise((resolve, reject) => {
    const worker = spawn(pythonCommand, [workerPath], {
      cwd: path.dirname(workerPath),
      stdio: ["pipe", "pipe", "pipe"],
      windowsHide: true
    });

    let stdout = "";
    let stderr = "";
    let settled = false;

    const timeout = setTimeout(() => {
      worker.kill();
      finishWithError(new Error("Selenium worker timed out"));
    }, 120000);

    function finishWithError(error) {
      if (settled) return;
      settled = true;
      clearTimeout(timeout);
      reject(error);
    }

    worker.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    worker.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    worker.on("error", (error) => {
      finishWithError(
        new Error(`Could not start Python: ${error.message}`)
      );
    });

    worker.on("close", (code) => {
      if (settled) return;

      clearTimeout(timeout);

      if (code !== 0) {
        finishWithError(
          new Error(
            `Selenium worker exited with code ${code}. ${stderr}`
          )
        );
        return;
      }

      try {
        const result = JSON.parse(stdout.trim());
        settled = true;
        resolve(result);
      } catch (error) {
        finishWithError(
          new Error(
            `Worker did not return valid JSON. Output: ${stdout}. Logs: ${stderr}`
          )
        );
      }
    });

    // Send the test case to Python through stdin.
    worker.stdin.on("error", (error) => {
      finishWithError(
        new Error(`Could not send test to worker: ${error.message}`)
      );
    });

    worker.stdin.end(JSON.stringify(testCase));
  });
}

module.exports = { runSeleniumTest };
