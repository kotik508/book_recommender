document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".pick-btn").forEach(button => {
        button.addEventListener("click", function () {
            let bookId = this.getAttribute("data-book-id");
            let bookItem = this.closest(".book-entry"); // Get the parent <li>

            console.log("Book selected:", bookId);

            // Create a new list item to be added to the lower section
            let pickedBookItem = bookItem.cloneNode(true); // Clone the selected book item

            // Append the selected book to the "Picked Books" section
            let lowerSection = document.querySelector(".lower-section ul");
            lowerSection.appendChild(pickedBookItem);

            // Optionally, you can remove the book from the upper section
            if (bookItem) {
                bookItem.remove();
            }

            // Send the POST request to Flask
            fetch("/books", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ book_id: bookId })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Response:", data);
                // Optionally, you can display a message or update the UI further
            })
            .catch(error => console.error("Error:", error));
        });
    });
});