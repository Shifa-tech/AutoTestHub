const TestCase = require("../models/Testcase");
const { runTestExecution } = require('../services/executionService');

const createTest = async (req, res) => {
    try {
        const test = await TestCase.create(req.body);

        res.status(201).json({
            success: true,
            data: test
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

const getTests = async (req, res) => {
    try {
        const tests = await TestCase.find().sort({ createdAt: -1 });

        res.json({
            success: true,
            data: tests
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
};

const runTest = async (req, res) => {
    try {
        const testId = req.params.id;
        const testCase = await TestCase.findById(testId);
        
        if (!testCase) {
            return res.status(404).json({ success: false, message: "Test case not found" });
        }

        const executionResult = await runTestExecution(testCase);
        
        res.status(200).json({
            success: true,
            data: executionResult
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: "Execution failed",
            details: error.message
        });
    }
};

module.exports = {
    createTest,
    getTests,
    runTest 
};