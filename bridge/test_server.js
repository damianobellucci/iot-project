var express = require('express');
var app = express();
const PORT = 3790;

app.get("/get", function (req, res) {
    res.send("ok");
})

app.listen(3790, () => console.log("connected, port: ", PORT))