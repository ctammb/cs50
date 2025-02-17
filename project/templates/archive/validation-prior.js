function validateForm() {
    const registrationForm = document.form['RegForm']
    const usernameFormElement = registrationForm['username']
    const username =
        document.getElementById("username").value;
    const firstname =
        document.getElementById("firstname").value;
    const email =
        document.getElementById("email").value;
    const role_id =
        document.getElementById("role_id").value;
    const phone =
        document.getElementById("phone").value;
    const password =
        document.getElementById("password").value;
    const confirmation =
        document.getElementById("confirmation").value;

    const usernameError =
        document.getElementById("username-error");
    const firstnameError =
        document.getElementById("firstname-error");
    const emailError =
        document.getElementById("email-error");
    const roleError =
        document.getElementById("role-error");
    const phoneError =
        document.getElementById("phone-error");
    const passwordError =
        document.getElementById("password-error");
    const confirmationError =
        document.getElementById("confirmation-error");

    usernameError.textContent = "";
    firstnameError.textContent = "";
    emailError.textContent = "";
    roleError.textContent = "";
    phoneError.textContent = "";
    passwordError.textContent = "";
    confirmationError.textContent = "";

    let isValid = true;

    if (username === "" || /\d/.test(name)) {
        usernameError.textContent =
            "Username required";
        isValid = false;
    }

    axios.post('/validate_registration', {
        username: username
    })
    .then((response) => {
        if (response.data.user_exists == "true") {
            usernameFormElement.setCustomValidity("Username already exists")
            usernameFormElement.reportValidity()
        }
    }, (error) => {
        console.log(error)
    }
    })

    if (firstname === "") {
        firstnameError.textContent =
            "First name required";
        isValid = false;
    }

    if (email === "" || !email.includes("@")) {
        emailError.textContent =
            "Please enter a valid email address.";
        isValid = false;
    }

    if (role_id === "") {
        roleError.textContent =
            "Role required";
        isValid = false;
    }

    if (phone === "") {
        phoneError.textContent =
            "Please enter a valid phone number";
        isValid = false;
    }

    if (password === "" || password.length < 6) {
        passwordError.textContent =
            "Please enter a password with at least 6 characters";
        isValid = false;
    }

    if (confirmation != password) {
        confirmationError.textContent =
            "Confirmation must match password";
        isValid = false;
    }

    return isValid;
    }
