function attemptRegister() {
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
            password: fields[2]
        }
        fetch("http://localhost:5000/create_account", {
            method: "POST",
            body: JSON.stringify(fetchBody),
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin":"*"
            }
        }).then((res) => {
            console.log(res.status)
            if (res.status == 201) {
                window.location.href = "/login?newAccount"
            }
            else if (res.status == 302) {
                alert(`Another account is using '${fields[1]}'!`)
            }
        })
    }
}

function githubOAuth() {
    document.location.href = "https://github.com/login/oauth/authorize?scope=user&client_id=Ov23li9VmFHDcHrC8c7a"
}

function onSignIn(googleUser) {
    console.log("Authenticated with Google");
    var profile = googleUser.getBasicProfile();
    console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
    console.log('Name: ' + profile.getName());
    console.log('Image URL: ' + profile.getImageUrl());
    console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.
    
}
