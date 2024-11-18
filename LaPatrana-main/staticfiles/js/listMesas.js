document.addEventListener('DOMContentLoaded', async () => {
    await listMesas();
});

const listMesas = async () => {
    try {
        const response = await fetch('/listMesas/');
        const data = await response.json();

        // Selecciona el contenedor donde se mostrarán las tarjetas de mesa
        const mesasContainer = document.getElementById('mesasContainer');

        // Recorre los datos de las mesas y crea una tarjeta para cada una
        data.mesa.forEach(mesa => {
            // Crea un elemento de div para las tarjeta de la mesa
            const cardDiv = document.createElement('div');
            cardDiv.classList.add('col-md-4');

            // Construye la URL para el enlace "Ver Pedido" con el ID de la mesa
            const verPedidoURL = `/verPedido/${mesa.idMesa}`;
            const tomarPedidoURL = `/tomarPedido/${mesa.idMesa}`;

            // Crea el contenido HTML de la tarjeta
            cardDiv.innerHTML = `
                <div class="card mt-2">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title text-center mb-4">Mesa ${mesa.idMesa}</h5>
                        <img src="/static/img/mesa.jpeg" alt="Imagen de la mesa" class="card-img-top" id="imagenMesa">
                        <div class="d-flex justify-content-between mb-4">
                            <a href="${tomarPedidoURL}" class="btn btn-success">Realizar pedido</a>
                            <a href="${verPedidoURL}" class="btn btn-warning">Ver pedido</a>
                        </div>
                    </div>
                </div>
            `;

            // Agrega la tarjeta al contenedor de las mesas
            mesasContainer.appendChild(cardDiv);
        });

    } catch (ex) {
        alert(ex);
    }
}

