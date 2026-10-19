const express = require("express");
const { createTest, getTests, runTest } = require('../controllers/testController');

const router = express.Router();

router.post("/", createTest);
router.get("/", getTests);
router.post("/:id/run", runTest);
module.exports = router;