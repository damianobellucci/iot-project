var mqtt = require('mqtt');

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
var counter = 0

var client = mqtt.connect(IPbroker, options);

client.on("connect", function () {
    console.log("-pub connection: " + client.connected);

})

client.on("error", function (error) {
    console.log("Can't connect" + error);
    process.exit(1)
});

setInterval(() => {
    if (client.connected == true) {
        counter++;
        string = "6000;10.24;15.12;12.33;25.29222222;"

        client.publish(topic_1, string.toString(), options);
        console.log('-published: ' + counter)
    }
    else {
        console.log("-pub connection: " + client.connected);
    }
}, 3000);
