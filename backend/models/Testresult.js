const mongoose = require("mongoose");

const testResultSchema = new mongoose.Schema(
    {
        testCaseId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "TestCase",
            required: true
        },

        status: {
            type: String,
            enum: ["PASSED", "FAILED"],
            required: true
        },

        executionTime: {
            type: Number
        },

        screenshot: {
            type: String
        },

        message: {
            type: String
        },

        errorMessage: {
            type: String
        }
    },
    {
        timestamps: true
    }
);

module.exports = mongoose.model("TestResult", testResultSchema);