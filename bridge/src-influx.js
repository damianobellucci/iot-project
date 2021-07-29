const { InfluxDB } = require('@influxdata/influxdb-client')

// You can generate a Token from the "Tokens Tab" in the UI
const token = 'VDO-0ZVFllIx3vpmto_WEFHkV6pIKmUDGSkhpkB7YCpmRvcSIq6snL-fLw0psiH23_EpWpH0MZ32ymRyfOLfoQ=='
const org = 'damiano'
const bucket = 'damiano'

const client = new InfluxDB({ url: 'http://localhost:8086', token: token })

const { Point } = require('@influxdata/influxdb-client')
const writeApi = client.getWriteApi(org, bucket)
writeApi.useDefaultTags({ id: 'host1', gps: "aaaa" })

const point = new Point('mem')
    .floatField('temperature', 23.43234543)

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