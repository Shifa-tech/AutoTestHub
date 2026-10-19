const TestCase = require("../models/Testcase");

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

module.exports = {
    createTest,
    getTests
};