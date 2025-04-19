var questionModal = document.getElementById("questionModal");
var myModal = document.getElementById("myModal");
var closeButton = document.getElementsByClassName("close")[0];
var closeButton2 = document.getElementsByClassName("close")[1];

window.onload = function () {
    questionModal.style.display = "block";
    myModal.style.display = "none";
};

document.getElementById("questionForm").onsubmit = function (event) {
    event.preventDefault();
    
    var formData = new FormData(document.getElementById("questionForm"));

    fetch("/final", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        questionModal.style.display = "none";
        myModal.style.display = "block";
    })
    .catch(error => {
        console.error('Error:', error);
    });
};


closeButton.onclick = function () {
    myModal.style.display = "none";
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
        myModal.style.display = "none";
    })
    .catch(error => {
        console.error('Error:', error);
    });
};
