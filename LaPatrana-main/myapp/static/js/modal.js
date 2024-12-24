document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("modal");
    const closeBtn = document.querySelector(".close-btn");

    // Mostrar el modal después de 3 segundos
    setTimeout(() => {
        modal.classList.add("visible");
    }, 3000);

    // Cerrar el modal
    closeBtn.addEventListener("click", () => {
        modal.classList.remove("visible");
    });

    // Cerrar modal al hacer clic fuera de él
    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.remove("visible");
        }
    });
});
