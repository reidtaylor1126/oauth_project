
cookies = extractCookies();

console.log(cookies)
if (cookies.token == null) {
    // document.location.replace("login")
} else {
    fetch(`http://localhost:5000/account_info`, {
        method: 'GET',
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Authorization": cookies.token
        },
    }).then((res) => {
        if (res.ok) {
            res.json().then((data) => {
                console.log(data)
                document.getElementById('welcome').innerText = `Welcome, ${data.fullname}!`
                document.getElementById('email').innerText = `Your email address is: ${data.email}`
            })
        }
    })
}

function attemptChangePW() {
    const inputs = [
        {name: "password1", minLen: 8},
        {name: "password2", minLen: 8},
        {name: "newPassword", minLen: 8},
    ]

    const fields = verifyForm("changePasswordForm", inputs);

    if(fields != null) {
        console.log(fields)

        if(fields[0] != fields[1]) {
            alert("Passwords do not match!");
            return;
        }
        if(fields[0] == fields[2]) {
            alert("New password must be different from the current password!")
            return;
        }

        fetchBody = {
            current_password: fields[0],
            new_password: fields[2]
        }
        console.log(fetchBody)
        fetch("http://localhost:5000/change-password", {
            method: "POST",
            body: JSON.stringify(fetchBody),
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin":"*",
                "Authorization": cookies.token
            }
        }).then((res) => {
            if(res.ok) {
                alert("Successfully changed password!")
            } else {
                window.location.replace("login.html?loggedOut=true")
            }
        })
    }
}

function logOut() {
    fetch("http://localhost:5000/logout", {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Authorization": cookies.token
        }
    }).then((res) => {
        if (res.ok) {
            document.cookie = "userId=-1"
            document.cookie = "token=*"
            window.location.href = "login"
        }
    })
}