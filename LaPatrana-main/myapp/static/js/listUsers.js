$.ajax({
    url: '/listUsers/', // Endpoint para obtener la lista de usuarios
    method: 'GET',
    success: function (response) {
        console.log("Datos recibidos:", response.users); // Accede a la clave 'users'
        
        // Verifica si hay usuarios registrados
        const data = response.users;
        if (!data || data.length === 0) {
            alert("No hay usuarios registrados.");
            return;
        }

        // Inicializa DataTable y limpia los datos actuales
        const dataTable = $('#datatable-users').DataTable();
        dataTable.clear();

        // Agrega los usuarios a la tabla
        data.forEach(user => {
            dataTable.row.add([
                user.id,                              // Columna 1: ID
                user.is_active ? "Sí" : "No",         // Columna 2: Activo
                user.email,                           // Columna 3: Email
                user.first_name,                      // Columna 4: Nombre
                user.last_name,                       // Columna 5: Apellido
                user.username,                        // Columna 6: Usuario
                user.type,                            // Columna 7: Tipo
                `
                <button class="btn btn-primary btn-sm" onclick="editarUsuario(${user.id})">Editar</button>
                <button class="btn btn-danger btn-sm" onclick="eliminarUsuario(${user.id})">Eliminar</button>
                `                                   // Columna 8: Botones de acción
            ]);
        });

        // Redibuja la tabla con los datos nuevos
        dataTable.draw();
    },
    error: function (err) {
        console.error("Error al obtener usuarios:", err);
        alert("Error al cargar los usuarios. Revisa la consola para más detalles.");
    }
});

// Función para manejar la edición de un usuario
function editarUsuario(userId) {
    console.log(`Editar usuario con ID: ${userId}`);
    // Aquí puedes implementar lógica para abrir un modal o redirigir a la página de edición
}

// Función para manejar la eliminación de un usuario
function eliminarUsuario(userId) {
    if (confirm("¿Estás seguro de que quieres eliminar este usuario?")) {
        $.ajax({
            url: `/deleteUser/${userId}/`,
            method: 'GET',
            success: function (response) {
                if (response.success) {
                    alert(response.message);
                    location.reload(); // Recarga la página para reflejar los cambios
                } else {
                    alert("Error al eliminar el usuario: " + response.error);
                }
            },
            error: function (err) {
                console.error("Error al eliminar usuario:", err);
                alert("Error al intentar eliminar el usuario.");
            }
        });
    }
}
