/*************************************************/
var express = require('express')
var app = express()
const PORT = 5021


app.post('/setparameters', function (req, res) {
    settingParameters = req.query;
    console.log("arrived request: ", settingParameters)

    const valid = validate(settingParameters)
    if (!valid) {
        console.log(validate.errors)
        res.send(validate.errors)
    }
    else {

        if (!isNumeric(settingParameters.sampleFrequency)
            ||
            !isNumeric(settingParameters.minTemp)
            ||
            !isNumeric(settingParameters.maxTemp)
            ||
            !isNumeric(settingParameters.minMoi)
            ||
            !isNumeric(settingParameters.maxMoi)
        ) {
            res.send({ "error": "parameters must be numbers" })
        }
        else {
            settingParameters.sampleFrequency = parseInt(settingParameters.sampleFrequency)
            settingParameters.minTemp = parseInt(settingParameters.minTemp)
            settingParameters.maxTemp = parseInt(settingParameters.maxTemp)
            settingParameters.minMoi = parseInt(settingParameters.minMoi)
            settingParameters.maxMoi = parseInt(settingParameters.maxMoi)

            if (settingParameters.sampleFrequency <= 0) {
                res.send({ error: "sampleFrequency must be more than zero." })
            }
            else {
                if (settingParameters.minMoi < 0) {
                    res.send({ error: "minMoi must be more or equal to zero." })
                }
                else {
                    if (settingParameters.minMoi > settingParameters.maxMoi) {
                        res.send({ error: "minMoi must be less or equal than maxMoi." })
                    }
                    else {
                        if (settingParameters.minMoi > settingParameters.maxMoi) {
                            res.send({ error: "minMoi must be less or equal than maxMoi." })
                        }
                        else {
                            if (settingParameters.minTemp < -40) {
                                res.send({ error: "minTemp must be more or equal to -40." })
                            }
                            else {
                                if (settingParameters.minTemp > 125) {
                                    res.send({ error: "minTemp must be less or equal to 125." })
                                }
                                else {
                                    if (settingParameters.minTemp > settingParameters.maxTemp) {
                                        res.send({ error: "minTemp must be less than maxTemp." })
                                    }
                                    else {
                                        string = settingParameters.sampleFrequency + ";" + settingParameters.minTemp + ";" + settingParameters.maxTemp + ";" + settingParameters.minMoi + ";" + settingParameters.maxMoi;

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
                                        }
                                    }
                                }
                            }

                        }
                    }
                }

            }
        }
    }

});

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
    "anyOf": [
        { "required": ["sampleFrequency"] },
        { "required": ["minTemp"] },
        { "required": ["maxTemp"] },
        { "required": ["minMoi"] },
        { "required": ["maxMoi"] }
    ]
}

const validate = ajv.compile(schema)

function isNumeric(num) {
    return !isNaN(num)
}
/**************** */