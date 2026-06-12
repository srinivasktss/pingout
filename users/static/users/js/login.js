document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
    const errorBox = document.getElementById("login-errors");
    const errorMessage = document.getElementById("login-error-message");

    if (!form) {
        return;
    }

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        hideError();

        const payload = {
            username: form.username.value.trim(),
            password: form.password.value,
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
                    showError(data.detail || "Login failed. Please try again.");
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
