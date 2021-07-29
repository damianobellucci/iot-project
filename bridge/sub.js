////////////////////////////////////////
const { InfluxDB } = require('@influxdata/influxdb-client')

// You can generate a Token from the "Tokens Tab" in the UI
const token = 'VDO-0ZVFllIx3vpmto_WEFHkV6pIKmUDGSkhpkB7YCpmRvcSIq6snL-fLw0psiH23_EpWpH0MZ32ymRyfOLfoQ=='
const org = 'damiano'
const bucket = 'damiano'

const { Point } = require('@influxdata/influxdb-client')

////////////////////////////////////////



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

    const client = new InfluxDB({ url: 'http://localhost:8086', token: token })

    const writeApi = client.getWriteApi(org, bucket)
    writeApi.useDefaultTags({ id: 'host1', gps: "aaaa" })

    let m = message.toString();

    let data = m.split(";");



    for (let i = 0; i < data.length; i++) {
        const point = new Point('mem');
        if (data[i] != undefined) {
            let info;
            if (i == 0) {
                info = 'temperature';
                point.floatField(info, data[i])
            }
            else if (i == 1) {
                info = 'humidity';
                point.floatField(info, data[i])
            }
            else if (i == 2) {
                info = 'soil_mosture';
                point.floatField(info, data[i])
            }
            else if (i == 3) {
                info = 'GPS';
                point.floatField(info, data[i].toString())
            }
            else if (i == 4) {
                info = 'rssi';
                point.floatField(info, data[i])
            }


            writeApi.writePoint(point)
            writeApi
                .close()
                .then(() => {
                    console.log('FINISHED')
                })
                .catch(e => {
                    console.error(e)
                    console.log('\\nFinished ERROR')
                })
        }



        console.log("topic: " + topic + " | message: " + message);
        //console.log(packet)
    }
});

client.subscribe(topic_1, options)


