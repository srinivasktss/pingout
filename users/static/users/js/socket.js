document.addEventListener("DOMContentLoaded", () => {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${protocol}://${window.location.host}/ws/main`;

    const socket = new WebSocket(socketUrl);

    socket.addEventListener("open", () => {
        console.log("WebSocket connected");
    });

    socket.addEventListener("message", (event) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
            case "new_message":
                // TODO: append the message to #chat-messages if it belongs
                // to the currently open conversation, otherwise update the
                // conversation list / unread badge.
                break;

            case "message_sent":
                // TODO: confirm a message we sent was saved (e.g. swap a
                // temporary/optimistic message for the real one).
                break;

            case "presence":
                // TODO: update online/offline indicator for data.user_id.
                break;

            case "unread_count":
                // TODO: update the unread badge for a conversation.
                break;

            default:
                console.log("Unhandled WebSocket message:", data);
        }
    });

    socket.addEventListener("close", () => {
        console.log("WebSocket disconnected");
    });

    socket.addEventListener("error", (event) => {
        console.error("WebSocket error", event);
    });

    window.chatSocket = socket;
});
