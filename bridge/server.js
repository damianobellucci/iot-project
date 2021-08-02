/*************************************************/
var fs = require('fs')
var express = require('express')
var app = express()
const PORT = 3450



const axios = require('axios')


const configHeaders = {
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
}



var stringSettingParameters;


app.post('/setparameters', function (req, res) {
    settingParameters = req.query;
    console.log("arrived request: ", settingParameters)

    console.log("ciao")
    const valid = validate(settingParameters)
    if (!valid) {
        console.log(validate.errors)
        res.send(validate.errors)
    }
    else {

        if (!settingParameters.hasOwnProperty("sampleFrequency") && !settingParameters.hasOwnProperty("minTemp") && !settingParameters.hasOwnProperty("maxTemp") && !settingParameters.hasOwnProperty("minMoi") && !settingParameters.hasOwnProperty("maxMoi")) {
            res.send({ error: "at least one parameter must be setted." })
        }
        else {



            if (
                (settingParameters.hasOwnProperty("sampleFrequency") && !isNumeric(settingParameters.sampleFrequency))
                ||
                (settingParameters.hasOwnProperty("minTemp") && !isNumeric(settingParameters.minTemp))
                ||
                (settingParameters.hasOwnProperty("maxTemp") && !isNumeric(settingParameters.maxTemp))
                ||
                (settingParameters.hasOwnProperty("minMoi") && !isNumeric(settingParameters.minMoi))
                ||
                (settingParameters.hasOwnProperty("maxMoi") && !isNumeric(settingParameters.maxMoi))
            ) {
                res.send({ "error": "parameters must be numbers" })
            }
            else {
                fs.readFile('./config.json', function read(err, data) {
                    if (err) {
                        throw err;
                    }
                    let fileSettingParameters = JSON.parse(data);
                    console.log("asd", fileSettingParameters)

                    //sovrascrizione parametri
                    settingParameters.hasOwnProperty("sampleFrequency") ? settingParameters.sampleFrequency = parseInt(settingParameters.sampleFrequency) : null
                    settingParameters.hasOwnProperty("minTemp") ? settingParameters.minTemp = parseInt(settingParameters.minTemp) : null
                    settingParameters.hasOwnProperty("maxTemp") ? settingParameters.maxTemp = parseInt(settingParameters.maxTemp) : null
                    settingParameters.hasOwnProperty("minMoi") ? settingParameters.minMoi = parseInt(settingParameters.minMoi) : null
                    settingParameters.hasOwnProperty("maxMoi") ? settingParameters.maxMoi = parseInt(settingParameters.maxMoi) : null

                    try {
                        list.forEach(f => {
                            f(settingParameters)
                        })
                        fs.writeFile('./config.json', JSON.stringify(settingParameters), (err) => {
                            if (err) throw err;
                            console.log('The file has been saved!');
                            string = settingParameters.sampleFrequency + ";" + settingParameters.minTemp + ";" + settingParameters.maxTemp + ";" + settingParameters.minMoi + ";" + settingParameters.maxMoi + ";";
                            stringSettingParameters = string;
                            const params = new URLSearchParams()
                            params.append('message', string)

                            axios.post("http://192.168.1.30:80/post", params, configHeaders)
                                .then((result) => {
                                    console.log(result)
                                    res.send({ ack: '', committedRequest: "" })
                                })
                                .catch((err) => {
                                    res.send({ err: '' })
                                    console.log(err)
                                })
                        })
                    } catch (e) {
                        res.send(e.toString())
                    };

                });

            }
        }
    }
});



app.get('/getparameters', function (req, res) {

    fs.readFile('./config.json', function read(err, data) {
        if (err) {
            throw err;
        }
        data = (JSON.parse(data));
        console.log(data)
        final = data.sampleFrequency + ";" + data.minTemp + ";" + data.maxTemp + ";" + data.minMoi + ";" + data.maxMoi + ";";
        res.send(final);
    });

})

app.listen(PORT, () => {
    console.log("listening port ", PORT)
})


/*************************************************/
var mqtt = require('mqtt')
const IPbroker = 'mqtt://130.136.2.70:1883'
const topic_1 = 'damianobellucci/test_setting_parameters'
const options = {
    clientId: 'clientJSpub',
    protocolId: 'MQIsdp',
    protocolVersion: 3,
    connectTimeout: 1000,
    debug: true,
    username: 'IOTuser',
    password: 'IOTuser',
    retain: true,
    qos: 2 //perché voglio che parametri di settaggio arrivino al broker senza duplicati e senza dubbio che non siano arrivati
};
var client = mqtt.connect(IPbroker, options);


client.on('connect', function () {
    console.log("mqtt connected")
})

client.on("error", function (error) {
    console.log("Mqtt error: " + error);
});


/*************************************************/

const Ajv = require("ajv")
const ajv = new Ajv() // options can be passed, e.g. {allErrors: true}

const schema = {
    type: "object",
    properties: {
        sampleFrequency: { type: "string" },
        minTemp: { type: "string" },
        maxTemp: { type: "string" },
        minMoi: { type: "string" },
        maxMoi: { type: "string" }
    },
    additionalProperties: false,
    /*"anyOf": [
        { "required": ["sampleFrequency"] },
        { "required": ["minTemp"] },
        { "required": ["maxTemp"] },
        { "required": ["minMoi"] },
        { "required": ["maxMoi"] }
    ]*/
}

const validate = ajv.compile(schema)

function isNumeric(num) {
    return !isNaN(num)
}
/*****************/



//prendo vecchia config (da file ) e ci applico sopra quella nuova, a quella nuova applico il test e se c'è qualche errore faccio una throw
errors = {
    one: "minMoi and maxMoi values must be between zero and 100",
    two: "minMoi must be less than maxMoi",
    three: "minTemp and maxTemp values must be between -40 and 125",
    four: "minTemp must be less than maxTemp",
    five: "sampleFrequency must not be less than 100"
}

function test1(obj) {
    if (obj.minMoi < 0 || obj.minMoi > 100)
        throw (errors.one)
}

function test2(obj) {
    if (obj.minMoi > obj.maxMoi)
        throw (errors.two)
}

function test3(obj) {
    if (obj.minTemp < -40 || obj.maxTemp > 125)
        throw (errors.three)
}

function test4(obj) {
    if (obj.minTemp > obj.maxTemp)
        throw (errors.four)
}

function test5(obj) {
    if (obj.sampleFrequency <= 100)
        throw (errors.five)
}




list = [test1, test2, test3, test4, test5]


//let a = { "minMoi": 1, "maxMoi": 10, "minTemp": 1, "maxTemp": 3, "sampleFrequency": 4 }



/*
if (client.connected) {
client.publish(topic_1, string.toString(), options, function (err) {
    if (err) {
        res.send(err)
        console.log(err)
    }
    else {
        console.log('-published: ', string)
        res.send({ ack: '', committedRequest: string })
    }
});
}
else {
res.send({ failed: "something wrong in the server. Try again." })
}*/