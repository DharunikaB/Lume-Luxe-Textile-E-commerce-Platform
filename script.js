document.addEventListener("DOMContentLoaded", function () {
    let dropdowns = document.querySelectorAll(".dropdown > a");

    dropdowns.forEach(function (dropdown) {
        dropdown.addEventListener("click", function (event) {
            event.preventDefault();
            let submenu = this.nextElementSibling;
            if (submenu) {
                submenu.style.display = submenu.style.display === "block" ? "none" : "block";
            }
        });
    });

    document.addEventListener("click", function (event) {
        let isDropdown = event.target.closest(".dropdown");
        document.querySelectorAll(".dropdown-menu").forEach(menu => {
            if (!isDropdown || isDropdown.querySelector(".dropdown-menu") !== menu) {
                menu.style.display = "none";
            }
        });
    });
});
