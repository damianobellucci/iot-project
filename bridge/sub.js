var mqtt = require('mqtt');

const IPbroker = 'mqtt://130.136.2.70:1883'
const topic_1 = 'temperature/damianobellucci'
const options = {
    clientId: 'clientJSsub',
    protocolId: 'MQIsdp',
    protocolVersion: 3,
    connectTimeout: 1000,
    debug: true,
    username: 'IOTuser',
    password: 'IOTuser',
    qos: 2 //perché voglio che parametri di settaggio che arrivano dal broker arrivano senza duplicati e senza dubbio che non siano arrivati
};

var client = mqtt.connect(IPbroker, options);


client.on("connect", function () {
    console.log("connected: " + client.connected);
})

client.on("error", function (error) {
    console.log("Can't connect" + error);
    process.exit(1)
});

client.on('message', function (topic, message, packet) {
    console.log("topic: " + topic + " | message: " + message);
    console.log(packet)
});

client.subscribe(topic_1, options)
