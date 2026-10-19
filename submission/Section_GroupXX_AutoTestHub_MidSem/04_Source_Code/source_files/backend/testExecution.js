const mongoose = require('mongoose');
const { runTestExecution } = require('./services/executionService');
const TestCase = require('./models/Testcase'); // Using Member 2's actual model

async function runStandaloneTest() {
    try {
        // 1. Connect to your local MongoDB instance
        console.log("Connecting to MongoDB...");
        // Update this URI if Member 2 used a different database name in their .env
        await mongoose.connect('mongodb://127.0.0.1:27017/autotesthub');
        console.log("Connected successfully.");

        // 2. Create a real Test Case in the database
        console.log("Creating a mock test case...");
        const mockTest = await TestCase.create({
            name: "Full Integration Pipeline Test",
            url: "https://example.com",
            actions: [{ type: "OPEN_URL" }]
        });
        console.log(`Test case saved to DB with ID: ${mockTest._id}`);

        // 3. Run your execution service (This spawns Python)
        console.log("Spawning Python execution service...");
        const result = await runTestExecution(mockTest);

        // 4. Output the final saved result
        console.log("Execution finished! Result saved to DB:");
        console.log(result);

    } catch (error) {
        console.error("Test execution failed:", error);
    } finally {
        // 5. Disconnect and exit
        await mongoose.disconnect();
        console.log("Disconnected from MongoDB. Exiting.");
        process.exit(0);
    }
}

runStandaloneTest();