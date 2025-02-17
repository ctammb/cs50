function validateUser() {
    const registrationForm = document.forms['RegForm'];
    const usernameFormElement = registrationForm['username'];
    const username = usernameFormElement.value;
    axios.post('/validate_registration', {
        username: username
    })
    .then((response) => {
        if (response.data.user_exists == "true") {
            usernameFormElement.setCustomValidity("Username already exists")
            usernameFormElement.reportValidity()
        }
    },  (error) => {
        console.log(error)
    })

}

function validateEmail() {
    const registrationForm = document.forms['RegForm']
    const emailFormElement = registrationForm['email']
    const email = emailFormElement.value
    if (email === "" || !email.includes("@")) {
        emailFormElement.setCustomValidity("Invalid email address")
        emailFormElement.reportValidity()
    }
}

function validateConfirmation() {
    const registrationForm = document.forms['RegForm']
    const passwordFormElement = registrationForm['password']
    const confirmationFormElement = registrationForm['confirmation']
    const password = passwordFormElement.value
    const confirmation = confirmationFormElement.value

    if (password != confirmation) {
            confirmationFormElement.setCustomValidity("Password does not match confirmation")
            confirmationFormElement.reportValidity()
    }
}

document.addEventListener("DOMContentLoaded", (event) => {
    console.log("DOM fully loaded and parsed");
  });
