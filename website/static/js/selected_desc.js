document.addEventListener("DOMContentLoaded", function () {
    const options = document.querySelectorAll(".description-btn");
    const inputs = document.querySelectorAll("input[name='answer']");
    const submitButton = document.getElementById("submit-btn");
    const buttons = document.querySelectorAll(".pick-btn");

    const form = document.querySelector("form");
    const bookIdsInput = document.getElementById("book_ids");

    form.addEventListener("submit", function () {
        let bookIds = [];

        document.querySelectorAll(".best-books .upper-section .pick-btn").forEach(button => {
            bookIds.push(button.getAttribute("data-book-id"));
        });

        bookIdsInput.value = bookIds.join(",");
    });

    inputs.forEach((input, index) => {
        input.addEventListener("change", function () {
            options.forEach(btn => btn.classList.remove("selected"));
            options[index].classList.add("selected");
            submitButton.disabled = false;
        });
    });

    buttons.forEach(button => {
        button.addEventListener("mouseenter", function () {
            document.querySelectorAll(".tooltip").forEach(t => t.remove());

            const title = this.dataset.title || "Unknown Title";
            const fullDescription = this.dataset.bookDesc || "No description available";
            const readMoreUrl = "https://www.goodreads.com/book/show/" + this.dataset.goodreadsId || "#";
            const maxLength = 200;
            let truncatedDescription = fullDescription;
            
            if (fullDescription.length > maxLength) {
                truncatedDescription = fullDescription.substring(0, maxLength) + '... ' + 
                    `<a href="${readMoreUrl}" class="read-more" target="_blank">Read more</a>`;
            }

            const tooltip = document.createElement("div");
            tooltip.classList.add("tooltip");
            tooltip.innerHTML = `<strong style="display: block; font-size: 1rem; margin-bottom: 5px;">${title}</strong><span class="tooltip-text">${truncatedDescription}</span>`;
            document.body.appendChild(tooltip);

            Object.assign(tooltip.style, {
                position: "absolute",
                backgroundColor: "#F7E7CE",
                color: "#4A261A",
                padding: "8px",
                borderRadius: "5px",
                fontSize: "0.9rem",
                boxShadow: "0 0 5px rgba(0, 0, 0, 0.2)",
                zIndex: "1000",
                pointerEvents: "auto",
                maxWidth: "400px",
                whiteSpace: "normal",
                wordWrap: "break-word",
                opacity: "1",
                display: "block",
                transition: "opacity 0.2s ease-in-out",
            });

            const rect = this.getBoundingClientRect();
            const tooltipRect = tooltip.getBoundingClientRect();

            let leftPos = rect.left + window.scrollX + rect.width / 2 - tooltipRect.width / 2;
            let topPos = rect.top + window.scrollY - tooltipRect.height - 10;

            if (leftPos < 0) leftPos = 10;
            if (leftPos + tooltipRect.width > window.innerWidth) {
                leftPos = window.innerWidth - tooltipRect.width - 10;
            }
            if (topPos < 0) topPos = rect.bottom + window.scrollY + 10;

            tooltip.style.left = `${leftPos}px`;
            tooltip.style.top = `${topPos}px`;

            this.tooltip = tooltip;

            tooltip.addEventListener("mouseenter", function () {
                clearTimeout(tooltip.hideTimeout);
            });

            tooltip.addEventListener("mouseleave", function () {
                tooltip.hideTimeout = setTimeout(() => tooltip.remove(), 200);
            });
        });

        button.addEventListener("mouseleave", function () {
            if (this.tooltip) {
                this.tooltip.hideTimeout = setTimeout(() => {
                    if (this.tooltip) this.tooltip.remove();
                }, 200);
            }
        });
    });
});
