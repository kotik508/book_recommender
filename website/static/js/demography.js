var modal = document.getElementById("myModal");
var closeButton = document.getElementsByClassName("close")[0];

window.onload = function () {
    modal.style.display = "block";
};

closeButton.onclick = function () {
    modal.style.display = "none";
};

document.getElementById("infoForm").onsubmit = function (event) {
    event.preventDefault();

    var formData = new FormData(document.getElementById("infoForm"));

    fetch("/final", {
        method: "POST",
        body: formData
    })
    .then(response => response.json()) 
    .then(data => {
        console.log(data);

        modal.style.display = "none";

    })
    .catch(error => {
        console.error('Error:', error);
    });
};