document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("register-form");
    const errorBox = document.getElementById("register-errors");
    const errorMessage = document.getElementById("register-error-message");

    if (!form) {
        return;
    }

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        hideError();

        const password1 = form.password1.value;
        const password2 = form.password2.value;

        if (password1 !== password2) {
            showError("Passwords do not match.");
            return;
        }

        const payload = {
            username: form.username.value.trim(),
            email: form.email.value.trim(),
            password1: password1,
            password2: password2,
        };

        fetch(window.location.pathname, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": form.csrfmiddlewaretoken.value,
            },
            body: JSON.stringify(payload),
        })
            .then((response) => response.json().then((data) => ({ status: response.status, data })))
            .then(({ status, data }) => {
                if (status >= 200 && status < 300) {
                    window.location.href = form.dataset.redirectUrl;
                } else {
                    showError(data.detail || "Registration failed. Please try again.");
                }
            })
            .catch(() => showError("Something went wrong. Please try again."));
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorBox.hidden = false;
    }

    function hideError() {
        errorBox.hidden = true;
    }
});
