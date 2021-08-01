const Ajv = require("ajv")
const ajv = new Ajv() // options can be passed, e.g. {allErrors: true}

const schema = {
    type: "object",
    properties: {
        sampleFrequency: { type: "number" },
        minTemp: { type: "number" },
        maxTemp: { type: "number" },
        minMoi: { type: "number" },
        maxMoi: { type: "number" }
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


const valid = validate(data)
if (!valid) console.log(validate.errors)