document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("user-search");
    const resultsBox = document.getElementById("user-search-results");
    const chatWelcome = document.getElementById("chat-welcome");
    const chatBox = document.getElementById("chat-box");
    const chatHeaderAvatar = document.getElementById("chat-header-avatar");
    const chatHeaderName = document.getElementById("chat-header-name");

    if (!searchInput || !resultsBox) {
        return;
    }

    searchInput.addEventListener("keydown", (event) => {
        if (event.key !== "Enter") {
            return;
        }

        event.preventDefault();

        const query = searchInput.value.trim();

        if (!query) {
            hideResults();
            return;
        }

        searchUsers(query);
    });

    document.addEventListener("click", (event) => {
        if (!resultsBox.contains(event.target) && event.target !== searchInput) {
            hideResults();
        }
    });

    function searchUsers(query) {
        fetch(`/api/users/search?q=${encodeURIComponent(query)}`)
            .then((response) => response.json())
            .then((users) => renderResults(users))
            .catch(() => renderResults([]));
    }

    function renderResults(users) {
        resultsBox.innerHTML = "";

        if (!users.length) {
            const empty = document.createElement("div");
            empty.className = "search-no-results";
            empty.textContent = "No user found.";
            resultsBox.appendChild(empty);
            resultsBox.classList.add("is-visible");
            return;
        }

        users.forEach((user) => {
            const item = document.createElement("div");
            item.className = "search-result-item";

            const avatar = document.createElement("div");
            avatar.className = "avatar";
            avatar.textContent = user.username.charAt(0).toUpperCase();

            const name = document.createElement("span");
            name.className = "conversation-name";
            name.textContent = user.username;

            item.appendChild(avatar);
            item.appendChild(name);
            item.addEventListener("click", () => openChat(user));
            resultsBox.appendChild(item);
        });

        resultsBox.classList.add("is-visible");
    }

    function hideResults() {
        resultsBox.classList.remove("is-visible");
        resultsBox.innerHTML = "";
    }

    function openChat(user) {
        hideResults();
        searchInput.value = "";

        if (!chatBox || !chatWelcome) {
            return;
        }

        chatHeaderAvatar.textContent = user.username.charAt(0).toUpperCase();
        chatHeaderName.textContent = user.username;

        chatWelcome.hidden = true;
        chatBox.hidden = false;

        // TODO (backend): load this conversation's message history,
        // e.g. fetch(`/api/conversations/${user.id}/messages/`)
    }
});
