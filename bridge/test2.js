const axios = require('axios')




const config = {
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
}

const params = new URLSearchParams()
params.append('message', 'aaaaaaaaaaaaaaaaa')
axios.post("http://192.168.1.3:80/post", params, config)
    .then((result) => {
        console.log(result)
    })
    .catch((err) => {

    })