document.addEventListener("DOMContentLoaded", function () {
    const dropdown = document.querySelector(".dropdown");
    const dropdownContent = document.querySelector(".dropdown-content");

    dropdown.addEventListener("mouseover", function () {
        dropdownContent.style.display = "block";
    });

    dropdown.addEventListener("mouseout", function () {
        dropdownContent.style.display = "none";
    });
});
