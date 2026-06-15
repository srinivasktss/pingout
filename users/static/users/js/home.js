document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("user-search");
    const resultsBox = document.getElementById("user-search-results");
    const chatWelcome = document.getElementById("chat-welcome");
    const chatBox = document.getElementById("chat-box");
    const chatHeaderAvatar = document.getElementById("chat-header-avatar");
    const chatHeaderName = document.getElementById("chat-header-name");
    const chatMessages = document.getElementById("chat-messages");
    const chatInputForm = document.getElementById("chat-input-form");
    const chatInput = document.getElementById("chat-input");
    const conversationItems = document.querySelector(".conversation-items");
    const conversationsEmpty = document.getElementById("conversations-empty");

    const currentUsername = document.body.dataset.username;

    window.Pingout = window.Pingout || {};
    window.Pingout.currentUsername = currentUsername;
    window.Pingout.currentChatUser = null;
    window.Pingout.appendMessage = appendMessage;
    window.Pingout.openChat = openChat;

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
            item.addEventListener("click", () => {
                openChat(user);
                startConversation(user);
            });
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

        window.Pingout.currentChatUser = user;

        chatHeaderAvatar.textContent = user.username.charAt(0).toUpperCase();
        chatHeaderName.textContent = user.username;

        chatWelcome.hidden = true;
        chatBox.hidden = false;

        chatMessages.innerHTML = "";
        const empty = document.createElement("div");
        empty.className = "chat-messages-empty";
        empty.textContent = "No messages yet. Say hello!";
        chatMessages.appendChild(empty);

        // TODO (backend): load this conversation's message history,
        // e.g. fetch(`/api/conversations/${user.id}/messages/`)
    }

    function getCsrfToken() {
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : "";
    }

    function startConversation(user) {
        fetch("/api/conversation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({ user_id: user.id }),
        })
            .then((response) => response.json())
            .then((conversation) => addConversationToList(conversation, user))
            .catch(() => {});
    }

    function addConversationToList(conversation, user) {
        if (!conversationItems) {
            return;
        }

        const existing = conversationItems.querySelector(`[data-username="${user.username}"]`);
        if (existing) {
            setActiveConversation(existing);
            return;
        }

        if (conversationsEmpty) {
            conversationsEmpty.hidden = true;
        }

        const item = document.createElement("a");
        item.href = "#";
        item.className = "conversation-item";
        item.dataset.username = user.username;
        if (conversation && conversation.id) {
            item.dataset.conversationId = conversation.id;
        }

        const avatar = document.createElement("div");
        avatar.className = "avatar";
        avatar.textContent = user.username.charAt(0).toUpperCase();

        const info = document.createElement("div");
        info.className = "conversation-info";

        const name = document.createElement("span");
        name.className = "conversation-name";
        name.textContent = (conversation && conversation.conversation_name) || user.username;

        const preview = document.createElement("span");
        preview.className = "conversation-preview";
        preview.textContent = "Say hello!";

        info.appendChild(name);
        info.appendChild(preview);

        item.appendChild(avatar);
        item.appendChild(info);

        item.addEventListener("click", (event) => {
            event.preventDefault();
            openChat(user);
        });

        conversationItems.prepend(item);
        setActiveConversation(item);
    }

    function setActiveConversation(item) {
        if (!conversationItems) {
            return;
        }
        conversationItems.querySelectorAll(".conversation-item").forEach((el) => {
            el.classList.remove("active");
        });
        item.classList.add("active");
    }

    function appendMessage({ from, message }) {
        if (!chatMessages) {
            return;
        }

        const placeholder = chatMessages.querySelector(".chat-messages-empty");
        if (placeholder) {
            placeholder.remove();
        }

        const bubble = document.createElement("div");
        bubble.className = "chat-message" + (from === currentUsername ? " sent" : " received");
        bubble.textContent = message;

        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    if (chatInputForm) {
        chatInputForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const message = chatInput.value.trim();
            const recipient = window.Pingout.currentChatUser;

            if (!message || !recipient || !window.chatSocket) {
                return;
            }

            window.chatSocket.send(JSON.stringify({
                from: currentUsername,
                to: recipient.username,
                message: message,
            }));

            chatInput.value = "";
        });
    }
});
