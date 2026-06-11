document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("user-search");
    const resultsBox = document.getElementById("user-search-results");

    if (!searchInput || !resultsBox) {
        return;
    }

    let debounceTimer;

    searchInput.addEventListener("input", () => {
        const query = searchInput.value.trim();

        clearTimeout(debounceTimer);

        if (!query) {
            resultsBox.classList.remove("is-visible");
            resultsBox.innerHTML = "";
            return;
        }

        debounceTimer = setTimeout(() => {
            // TODO (backend): replace with a real search endpoint, e.g.
            // fetch(`/users/search/?q=${encodeURIComponent(query)}`)
            //   .then((res) => res.json())
            //   .then((users) => renderResults(users));
        }, 300);
    });

    document.addEventListener("click", (event) => {
        if (!resultsBox.contains(event.target) && event.target !== searchInput) {
            resultsBox.classList.remove("is-visible");
        }
    });

    function renderResults(users) {
        resultsBox.innerHTML = "";

        if (!users.length) {
            resultsBox.classList.remove("is-visible");
            return;
        }

        users.forEach((user) => {
            const item = document.createElement("a");
            item.href = `/chat/${user.id}/`;
            item.className = "conversation-item";
            item.innerHTML = `
                <div class="avatar">${user.username.charAt(0).toUpperCase()}</div>
                <div class="conversation-info">
                    <span class="conversation-name">${user.username}</span>
                </div>
            `;
            resultsBox.appendChild(item);
        });

        resultsBox.classList.add("is-visible");
    }
});
