const express = require("express");

const {
    createTest,
    getTests
} = require("../controllers/testController");

const router = express.Router();

router.post("/", createTest);
router.get("/", getTests);

module.exports = router;