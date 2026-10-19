const { spawn } = require('child_process');
const path = require('path');
const TestResult = require('../models/Testresult'); // Using Member 2's actual database model

async function runTestExecution(testCase) {
    return new Promise((resolve, reject) => {
        // Pointing to Member 3's actual Python script
        const scriptPath = path.join(__dirname, '../../selenium-worker/runner.py');
        
        // Spawn the Python process
        const pyProcess = spawn('python3', [scriptPath]);

        let outputData = '';
        let errorData = '';

        pyProcess.stdout.on('data', (data) => outputData += data.toString());
        pyProcess.stderr.on('data', (data) => errorData += data.toString());

        pyProcess.on('close', async (code) => {
            try {
                // Find the JSON block (ignores any WebDriver logs printed to stdout)
                const jsonMatch = outputData.match(/\{[\s\S]*\}/);
                if (!jsonMatch) {
                    throw new Error(`No JSON found in Python output. Stderr: ${errorData}`);
                }

                const resultPayload = JSON.parse(jsonMatch[0]);

                // Save to MongoDB using Member 2's model
                const newResult = new TestResult({
                    testCaseId: testCase._id,
                    status: resultPayload.status,
                    executionTime: resultPayload.executionTime,
                    screenshot: resultPayload.screenshot,
                    message: resultPayload.message,
                    errorMessage: resultPayload.errorMessage,
                    executedAt: new Date()
                });

                const savedResult = await newResult.save();
                resolve(savedResult);

            } catch (error) {
                console.error("Execution parsing failed:", error);
                
                // Fallback: Save a FAILED result if the integration breaks
                const failedResult = new TestResult({
                    testCaseId: testCase._id,
                    status: "FAILED",
                    executionTime: 0,
                    message: "Integration error or Python crash",
                    errorMessage: error.message,
                    executedAt: new Date()
                });
                
                const savedFailedResult = await failedResult.save();
                resolve(savedFailedResult);
            }
        });

       const payloadForPython = {
            testCaseId: testCase._id.toString(), // Convert Mongoose ObjectId to a plain string
            name: testCase.name,
            url: testCase.url,
            actions: testCase.actions
        };

        // Safely send the formatted JSON into Python
        pyProcess.stdin.write(JSON.stringify(payloadForPython));
        pyProcess.stdin.end();
    });
}

module.exports = { runTestExecution };