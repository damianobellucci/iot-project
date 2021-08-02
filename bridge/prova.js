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


let a = { "minMoi": 1, "maxMoi": 10, "minTemp": 1, "maxTemp": 3, "sampleFrequency": 4 }


list.forEach(f => {
    f(a)
})


