document.addEventListener("DOMContentLoaded", function () {
    const upperSection = document.querySelector(".upper-section ul");
    const lowerSection = document.querySelector(".lower-section ul");

    console.log('here')

    // Add event listener to the pick buttons in the upper section
    upperSection.addEventListener("click", function (event) {
        if (event.target.closest(".pick-btn")) {
            // Check if there are less than 5 books in the lower section
            if (lowerSection.children.length >= 5) {
                alert("You can't add more than 5 books to the lower section.");
                return; // Stop the function if there are already 5 books
            }

            let bookId = event.target.closest(".pick-btn").getAttribute("data-book-id");
            let bookItem = event.target.closest(".book-entry");

            console.log("Book selected:", bookId);

            // Clone the selected book item and move it to the lower section
            let pickedBookItem = bookItem.cloneNode(true);
            lowerSection.appendChild(pickedBookItem);

            // Remove the book from the upper section
            bookItem.remove();

            // Send the POST request to Flask
            fetch("/books", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ book_id: bookId, add: 'pick' })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Response:", data);
            })
            .catch(error => console.error("Error:", error));
        }
    });

    // Add event listener to the books in the lower section
    lowerSection.addEventListener("click", function (event) {
        // Ensure the clicked element is a book entry (button or parent)
        let bookItem = event.target.closest(".book-entry");
        if (bookItem) {
            let bookId = bookItem.querySelector(".pick-btn").getAttribute("data-book-id");

            console.log("Removing book from the lower section.");

            // Remove the book from the lower section
            bookItem.remove();

            // Send the POST request to Flask for removal
            fetch("/books", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ book_id: bookId, add: 'rm_pick' })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Response:", data);
            })
            .catch(error => console.error("Error:", error));
        }
    });
});
