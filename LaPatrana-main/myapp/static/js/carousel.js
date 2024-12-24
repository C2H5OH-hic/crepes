document.addEventListener("DOMContentLoaded", function () {
    const images = document.querySelectorAll(".hero-carousel img");
    let currentIndex = 0;

    function changeImage() {
        // Ocultar la imagen actual
        images[currentIndex].classList.remove("active");

        // Pasar a la siguiente imagen
        currentIndex = (currentIndex + 1) % images.length;

        // Mostrar la nueva imagen
        images[currentIndex].classList.add("active");
    }

    // Cambiar la imagen cada 5 segundos
    setInterval(changeImage, 5000);
});
