// Redirección al login
document.getElementById("login-btn").addEventListener("click", function() {
    window.location.href = loginUrl; // Usa la URL definida en la plantilla
});

// Redirección a productos públicos
document.getElementById("products-btn").addEventListener("click", function() {
    window.location.href = productosUrl; // Usa la URL definida en la plantilla
});