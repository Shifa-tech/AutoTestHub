const mongoose = require("mongoose");

const testCaseSchema = new mongoose.Schema(
    {
        name: {
            type: String,
            required: true
        },

        url: {
            type: String,
            required: true
        },

        actions: {
            type: Array,
            default: []
        },

        expectedResult: {
            type: String,
            default: ""
        }
    },
    {
        timestamps: true
    }
);

module.exports = mongoose.model("TestCase", testCaseSchema);