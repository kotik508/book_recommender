document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        let flashMessages = document.querySelectorAll(".flash-message");
        flashMessages.forEach(function (message) {
            message.classList.add("fade");
            setTimeout(() => message.remove(), 500);
        });
    }, 3000);
});