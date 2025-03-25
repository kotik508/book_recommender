document.addEventListener("DOMContentLoaded", function () {
    const upperSections = document.querySelectorAll(".upper-section ul");
    const leftList = document.querySelector(".left-list");
    const lowerSection = document.querySelector(".lower-section ul");

    console.log('here');

    upperSections.forEach(upperSection => {
        upperSection.addEventListener("click", function (event) {
            if (event.target.closest(".pick-btn")) {
                if (lowerSection.children.length >= 5) {
                    alert("You can't add more than 5 books to the lower section.");
                    return;
                }

                let bookItem = event.target.closest(".book-entry");
                let bookId = bookItem.querySelector(".pick-btn").getAttribute("data-book-id");

                console.log("Book selected:", bookId);

                let pickedBookItem = bookItem.cloneNode(true);
                lowerSection.appendChild(pickedBookItem);

                bookItem.remove();

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
    });

    lowerSection.addEventListener("click", function (event) {
        let bookItem = event.target.closest(".book-entry");
        if (bookItem) {
            let bookId = bookItem.querySelector(".pick-btn").getAttribute("data-book-id");

            console.log("Moving book back to the left list.");

            let returnedBookItem = bookItem.cloneNode(true);
            leftList.appendChild(returnedBookItem);

            bookItem.remove();

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
