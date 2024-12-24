document.addEventListener("DOMContentLoaded", function () {
    // Redirección para el botón "Iniciar Sesión"
    document.getElementById("login-btn").addEventListener("click", function () {
        window.location.href = loginUrl; // Redirige a la página de inicio de sesión
    });

    // Redirección para ambos botones de productos
    const productButtons = document.querySelectorAll("#products-btn, #view-products-btn");
    productButtons.forEach(button => {
        button.addEventListener("click", function () {
            window.location.href = productosUrl; // Redirige a la lista de productos
        });
    });

    // Animaciones al hacer scroll
    const elements = document.querySelectorAll(".fade-in");
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
            }
        });
    });

    elements.forEach((el) => observer.observe(el));
});
