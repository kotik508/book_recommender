document.addEventListener("DOMContentLoaded", function () {
    const upperSection = document.querySelector(".upper-section ul");
    const lowerSection = document.querySelector(".lower-section ul");

    // Function to add a new book to the upper section
    function addNewBookToUpperSection() {
        // Check if there are still books available to add
        if (best_books.length > 0) {
            let book = best_books.shift(); // Get the first book and remove it from the array

            // Create a new list item for the book
            let bookItem = document.createElement("li");
            bookItem.classList.add("book-entry");

            // Create the button with book information
            let button = document.createElement("button");
            button.classList.add("pick-btn");
            button.setAttribute("type", "button");
            button.setAttribute("data-book-id", book.id);

            let img = document.createElement("img");
            img.setAttribute("src", book.cover_image_uri);
            img.setAttribute("alt", book.title);
            img.classList.add("book-image");

            let span = document.createElement("span");
            span.textContent = book.title;

            // Append the button and its child elements
            button.appendChild(img);
            button.appendChild(span);
            bookItem.appendChild(button);

            // Append the new book to the upper section
            upperSection.appendChild(bookItem);
        }
    }

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
                body: JSON.stringify({ book_id: bookId, add: true })
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
                body: JSON.stringify({ book_id: bookId, add: false })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Response:", data);
            })
            .catch(error => console.error("Error:", error));
        }
    });
});
