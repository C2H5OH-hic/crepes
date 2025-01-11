document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.cambiar-estado-form').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            var estado = form.closest('tr').querySelector('.estado-pedido').textContent.trim();
            var nuevoEstado = estado === 'Listo' ? 'En proceso...' : 'Listo';
            Swal.fire({
                title: '¿Estás seguro?',
                text: `Cambiar el estado del pedido a "${nuevoEstado}"`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, cambiar estado',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                    Swal.fire({
                        title: 'Estado cambiado',
                        text: `El estado del pedido ha sido cambiado a "${nuevoEstado}"`,
                        icon: 'success',
                        timer: 20000, // Total duration set to 20 seconds (20000 milliseconds)
                        timerProgressBar: true,
                        showConfirmButton: false
                    });
                }
            });
        });
    });
});
