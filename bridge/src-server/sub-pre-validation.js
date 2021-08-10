////////////////////////////////////////
const { InfluxDB } = require('@influxdata/influxdb-client')

// You can generate a Token from the "Tokens Tab" in the UI
const token = '4pQidiCvurOgttstoaQIKrwUdk-9dnGxb4DBRXuqYX9JNE56KIsTSFxPaoP8RVEbxI2fFueACaP0C8U3d1iJgw=='
const org = 'damiano'
const bucket = 'rawdata'

const { Point } = require('@influxdata/influxdb-client')

////////////////////////////////////////



var mqtt = require('mqtt');

const IPbroker = 'mqtt://130.136.2.70:1883'
const topic_1 = 'damianobellucci/test'
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

    let m = message.toString();

    let data = m.split(";");



    for (let i = 0; i < data.length; i++) {
        const point = new Point('pre-validation');
        if (data[i] == undefined || data[i] == 'nan') {
            data[i] = 'null';
            if (i == 0) {
                info = 'temperature';
                console.log(data[i])
                point.floatField(info, data[i])
            }
            else if (i == 1) {
                info = 'humidity';
                point.floatField(info, data[i])
            }
            else if (i == 2) {
                info = 'id';
                point.floatField(info, data[i])
            }
            else if (i == 3) {
                info = 'GPS';
                point.floatField(info, data[i])

            }
            else if (i == 4) {
                info = 'RSSI';
                point.floatField(info, data[i])
            }
            else if (i == 5) {
                info = 'soil_moisture';
                point.floatField(info, data[i])
            }
            else if (i == 6) {
                info = 'SHI';
                point.floatField(info, data[i])
            }

            writeApi.useDefaultTags({ id: data[2], GPS: data[3].replace(",", ";") })



            writeApi.writePoint(point, { precision: 's' })
            writeApi
                .close()
                .then(() => {

                    //console.log('FINISHED')
                })
                .catch(e => {
                    console.error(e)
                    console.log('\\nFinished ERROR')
                })
        }




        //console.log(packet)
    }
    console.log("topic: " + topic + " | message: " + message);
});

client.subscribe(topic_1, options)


