function verifyProperty(form, inputName, length) {
    const formInput = form[inputName].value;
    if (formInput == "") {
        return(`${inputName} required!\n`);
    } else if (formInput.length < length) {
        return(`${inputName} must be at least ${length} characters!\n`);
    }
    return "";
}

function verifyForm(formName, inputs) {
    const form = document.forms[formName];
    console.log(form);
    let errors = "";
    const fields = [];

    for (formInput of inputs) {
        console.log(formInput);
        const propertyResult = verifyProperty(form, formInput.name, formInput.minLen)
        if (propertyResult != "") {
            errors += propertyResult;
        } else {
            fields.push(form[formInput.name].value)
        }
    }

    if (errors != "") {
        alert(errors);
        return null;
    } else {
        return fields;
    }
}

function extractCookies() {
    const cookie = document.cookie;
    const cookieStrings = cookie.split('; ')
    let cookies = {}
    for (const cookieStr of cookieStrings) {
        const kv = cookieStr.split('=')
        cookies[kv[0]] = kv[1]
    }
    return cookies;
}