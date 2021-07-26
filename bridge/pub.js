var mqtt = require('mqtt');

const IPbroker = 'mqtt://130.136.2.70:1883'
const topic_1 = 'temperature/damianobellucci'
const options = {
    clientId: 'clientJSpub',
    protocolId: 'MQIsdp',
    protocolVersion: 3,
    connectTimeout: 1000,
    debug: true,
    username: 'IOTuser',
    password: 'IOTuser',
    retain: true,
    qos: 1
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
        client.publish(topic_1, counter.toString(), options);
        console.log('-published: ' + counter)
    }
    else {
        console.log("-pub connection: " + client.connected);
    }
}, 3000);
