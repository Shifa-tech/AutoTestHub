const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

require("dotenv").config();

const connectDB = require("./config/database");
connectDB();

const testRoute = require("./routes/testRoute");
app.use("/api/tests", testRoute);

app.get("/api/health", (req, res) => {
    res.json({
        success: true,
        message: "AutoTestHub backend is running"
    });
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
    console.log(`Backend running on port ${PORT}`);
});
