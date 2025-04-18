cookies = extractCookies();
console.log(cookies);

document.cookie = "token=*" 

if (cookies.thirdParty != null) {
    document.getElementById("title").innerText = `Finish registering with ${cookies.thirdParty} integration:`
}

if (cookies.name != null) {
    input = document.getElementById("username")
    input.value = cookies.name;
    input.disabled = true;
}
if (cookies.email != null) {
    input = document.getElementById("email")
    input.value = cookies.email;
    input.disabled = true;
}

function finishRegistration() {
    const inputs = [
        {name: "username", minLen: 5},
        {name: "email", minLen: 8},
        {name: "password", minLen: 8},
    ]
    
    const fields = verifyForm("registerForm", inputs);

    if(fields != null) {
        console.log(fields)

        fetchBody = {
            fullname: fields[0],
            email: fields[1],
            password: fields[2],
            third_party_token: cookies.token,
            third_party: cookies.thirdParty
        }

        fetch("http://localhost:5000/registerFromExternal", {
            method: "POST",
            body: JSON.stringify(fetchBody),
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin":"*"
            }
        }).then((res) => {
            console.log(res.status)
            res.json().then((data) => {
                // console.log(data)
                document.cookie = `token=${data.token}`
                document.location.replace("account")
            })
        })
    }
}