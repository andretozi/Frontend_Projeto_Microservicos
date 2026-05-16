// projeto_github.js — extraído de templates/projeto/projeto_github.html

function toggleCompanyMenu() { document.getElementById("companyMenu").classList.toggle("show"); }
function toggleUserMenu() { document.getElementById("userMenu").classList.toggle("show"); }

window.addEventListener("click", function(e) {
    const userMenu = document.getElementById("userMenu");
    const userBtn = document.querySelector(".user-toggle");
    if (userMenu && userBtn && !userMenu.contains(e.target) && !userBtn.contains(e.target)) {
        userMenu.classList.remove("show");
    }
    const compMenu = document.getElementById("companyMenu");
    const compBtn = document.querySelector(".company-toggle");
    if (compMenu && compBtn && !compMenu.contains(e.target) && !compBtn.contains(e.target)) {
        compMenu.classList.remove("show");
    }
});
