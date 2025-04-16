function attemptLogin() {
    const inputs = [
        {name: "email", minLen: 8},
        {name: "password", minLen: 8},
    ]
    
    const fields = verifyForm("loginForm", inputs);

    if(fields != null) {
        console.log(fields)

        fetchBody = {
            email: fields[0],
            password: fields[1]
        }
        fetch("http://localhost:5000/login", {
            method: "POST",
            body: JSON.stringify(fetchBody),
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin":"*"
            }
        }).then((res) => {
            console.log(res.status)
            if (res.status == 200) {
                console.log(res)
                res.json().then((data) => {
                    console.log(data)
                    document.cookie = `userId=${data.user_id}`;
                    document.cookie = `token=${data.token}`
                    window.location.href = "account"
                })
            } else {
                alert(`Invalid credentials`)
            }
        })
    }
}

function githubOAuth() {
    document.location.href = "https://github.com/login/oauth/authorize?scope=user&client_id=Ov23li9VmFHDcHrC8c7a"
}

const urlParams = new Proxy(new URLSearchParams(window.location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
})

if (urlParams.newAccount) {
    document.getElementById("loginTitle").innerText = "Log in to your new account:"
} else if (urlParams.loggedOut) {
    alert("You were logged out due to suspicious activity!")
}
