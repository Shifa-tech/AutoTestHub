const TestCase = require("../models/Testcase");
const { runSeleniumTest } = require("../services/executionService");

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
    const test = await TestCase.findById(req.params.id);

    if (!test) {
      return res.status(404).json({
        success: false,
        message: "Test case not found"
      });
    }

    const result = await runSeleniumTest(test.toObject());

    return res.json({
      success: true,
      testId: test._id,
      result
    });
  } catch (error) {
    console.error("Test execution failed:", error.message);

    return res.status(500).json({
      success: false,
      message: "Test execution failed",
      error: error.message
    });
  }
};


module.exports = {
    createTest,
    getTests,runTest
};