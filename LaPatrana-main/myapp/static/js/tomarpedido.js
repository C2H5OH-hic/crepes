document.addEventListener('DOMContentLoaded', () => {
    let productosData;

    try {
        productosData = JSON.parse(document.getElementById('productos-data').textContent);
        console.log("🔹 Productos cargados en JS:", productosData);
    } catch (error) {
        console.error("❌ Error al parsear `productosData`: ", error);
        productosData = [];
    }

    const productosLista = document.getElementById('productos-lista');
    const listaIngredientes = document.getElementById('ingredientes-container');
    const modalIngredientes = document.getElementById('modal-ingredientes');
    const guardarIngredientesBtn = document.getElementById('guardar-ingredientes');
    const modalNotas = document.getElementById('modal-notas');
    const guardarNotasBtn = document.getElementById('guardar-nota');
    const notaTexto = document.getElementById('nota-texto');

    productosLista.addEventListener('click', function (event) {
        if (event.target.classList.contains('btn-notas')) {
            filaIdSeleccionada = event.target.getAttribute('data-fila-id');
    
            if (!window.combinacionesProductos[filaIdSeleccionada]) {
                console.warn(`⚠️ No se encontró la fila ${filaIdSeleccionada} en combinacionesProductos.`);
                return;
            }
    
            // Asignar la nota guardada al área de texto del modal
            notaTexto.value = window.combinacionesProductos[filaIdSeleccionada].nota || "";
    
            // Asignar la fila seleccionada al botón de guardar
            guardarNotasBtn.dataset.filaId = filaIdSeleccionada;
        }
    });
    
    // 🟢 Guardar la nota correctamente en cada producto sin interferencias
    guardarNotasBtn.addEventListener('click', function () {
        const filaId = this.dataset.filaId;
    
        if (filaId && window.combinacionesProductos[filaId]) {
            window.combinacionesProductos[filaId].nota = notaTexto.value;
            
            // Actualizar la interfaz con la nota guardada
            const notaElemento = document.getElementById(`nota_${filaId}`);
            if (notaElemento) {
                notaElemento.textContent = notaTexto.value || "Sin nota";
            } else {
                console.warn(`⚠️ No se encontró el elemento para mostrar la nota en fila: ${filaId}`);
            }
        }
    });
    
    const productoSeleccionado = document.getElementById('producto-seleccionado');
    const totalPedido = document.getElementById('total-pedido');
    
    // 📌 Definir `combinacionesProductos` en `window` para evitar errores de referencia
    window.combinacionesProductos = {};

    let filaIdSeleccionada = null;
    let filaIdIngredientes = null;

    if (productosData.length === 0) {
        console.warn("⚠️ Advertencia: No hay productos disponibles.");
        return;
    }

    productosLista.innerHTML = "";

    productosData.forEach(producto => {
        if (!producto.nombre || producto.precio === null) {
            console.warn(`⚠️ Producto inválido detectado en JS:`, producto);
            return;
        }
        agregarFilaProducto(producto);
    });

    function agregarFilaProducto(producto) {
        console.log("🛠️ Agregando producto a la tabla:", producto);

        const fila = document.createElement('tr');
        const idUnico = `${producto.idProducto}_${Date.now()}`;
        fila.dataset.filaId = idUnico;

        fila.innerHTML = `
            <td>${producto.nombre}</td>
            <td>${producto.categoria}</td>
            <td>$${producto.precio.toFixed(2)}</td>
            <td>
                <input type="number" class="form-control cantidad-producto" 
                       name="cantidad_${idUnico}" 
                       min="0" value="0" data-producto-id="${producto.idProducto}" data-precio="${producto.precio}">
            </td>
            <td>
                <button type="button" class="btn btn-secondary btn-sm btn-ingredientes" 
                        data-bs-toggle="modal" 
                        data-bs-target="#modal-ingredientes" 
                        data-fila-id="${idUnico}" 
                        data-producto-id="${producto.idProducto}" 
                        data-producto-nombre="${producto.nombre}">
                    Ingredientes
                </button>
            </td>
            <td>
                <button type="button" class="btn btn-info btn-sm btn-notas" 
                        data-bs-toggle="modal" 
                        data-bs-target="#modal-notas" 
                        data-fila-id="${idUnico}">
                    Nota
                </button>
                <span id="nota_${idUnico}" class="d-block text-muted">Sin nota</span>
            </td>
            <td class="subtotal-producto" id="subtotal_${idUnico}">$0.00</td>
        `;

        productosLista.appendChild(fila);

        window.combinacionesProductos[idUnico] = {
            productoId: producto.idProducto,
            ingredientes: {},
            cantidad: 0,
            precio: producto.precio,
            nota: ""
        };

        actualizarTotales();
    }

    function actualizarTotales() {
        let total = 0;
        Object.keys(window.combinacionesProductos).forEach(filaId => {
            const combinacion = window.combinacionesProductos[filaId];
            if (combinacion.cantidad > 0) {
                const subtotal = combinacion.cantidad * combinacion.precio;
                total += subtotal;

                const fila = document.querySelector(`[data-fila-id="${filaId}"]`);
                if (fila) {
                    const subtotalCell = fila.querySelector(`#subtotal_${filaId}`);
                    if (subtotalCell) {
                        subtotalCell.textContent = `$${subtotal.toFixed(2)}`;
                    }
                }
            }
        });

        totalPedido.textContent = total.toFixed(2);
    }

    productosLista.addEventListener('input', (event) => {
        if (event.target.classList.contains('cantidad-producto')) {
            const filaId = event.target.closest('tr').dataset.filaId;
            const cantidad = parseInt(event.target.value, 10);
            if (!isNaN(cantidad) && cantidad >= 0) {
                window.combinacionesProductos[filaId].cantidad = cantidad;
                actualizarTotales();
            }
        }
    });

    modalIngredientes.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        filaIdIngredientes = button.getAttribute('data-fila-id');
        const productoId = button.getAttribute('data-producto-id');
        const productoNombre = button.getAttribute('data-producto-nombre');

        productoSeleccionado.textContent = `Ingredientes adicionales para: ${productoNombre}`;
        listaIngredientes.innerHTML = '';

        const producto = productosData.find(p => p.idProducto === parseInt(productoId));
        if (!producto) {
            console.warn(`⚠️ No se encontró el producto con ID ${productoId}`);
            return;
        }

        for (let i = 0; i < window.combinacionesProductos[filaIdIngredientes].cantidad; i++) {
            const div = document.createElement('div');
            div.classList.add('mb-2');
            div.innerHTML = `<p><strong>Unidad ${i + 1}:</strong></p>`;

            producto.ingredientes_adicionales.forEach(ingrediente => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.innerHTML = `
                    <div class="form-check">
                        <input class="form-check-input ingrediente-check" type="checkbox" 
                               data-fila-id="${filaIdIngredientes}" 
                               data-unidad="${i}" 
                               value="${ingrediente.ingrediente__id}" 
                               data-nombre="${ingrediente.ingrediente__nombre}">
                        <label class="form-check-label">
                            ${ingrediente.ingrediente__nombre}
                        </label>
                    </div>
                `;
                div.appendChild(li);
            });

            listaIngredientes.appendChild(div);
        }
    });

    guardarIngredientesBtn.addEventListener('click', function () {
        const ingredientesSeleccionados = {};

        listaIngredientes.querySelectorAll('.ingrediente-check:checked').forEach(input => {
            const unidad = input.getAttribute('data-unidad');
            if (!ingredientesSeleccionados[unidad]) {
                ingredientesSeleccionados[unidad] = [];
            }
            ingredientesSeleccionados[unidad].push({
                id: input.value,
                nombre: input.dataset.nombre
            });
        });

        window.combinacionesProductos[filaIdIngredientes].ingredientes = ingredientesSeleccionados;
        console.log(`Ingredientes seleccionados para la fila ${filaIdIngredientes}:`, ingredientesSeleccionados);
    });

    console.log("🔹 DOM completamente cargado.");
    setTimeout(() => {
        const guardarPedidoBtn = document.getElementById("guardar-pedido");
        if (!guardarPedidoBtn) {
            console.error("❌ ERROR: No se encontró `guardar-pedido` en el DOM. Verifica que el botón existe en la plantilla HTML.");
            return;
        }

        guardarPedidoBtn.addEventListener("click", function(event) {
            event.preventDefault();
            guardarPedido();
        });
    }, 500);
    
    function guardarPedido() {
        let clienteNombre = document.getElementById("cliente-nombre").value;
        let productosSeleccionados = [];
    
        console.log("🔹 combinacionesProductos antes de enviar:", window.combinacionesProductos);
    
        Object.keys(window.combinacionesProductos).forEach(filaId => {
            let producto = window.combinacionesProductos[filaId];
    
            if (producto && parseInt(producto.cantidad) > 0) {
                let productoFinal = {
                    id: producto.productoId ? parseInt(producto.productoId) : null,  
                    cantidad: parseInt(producto.cantidad),  
                    nota: producto.nota || "",
                    ingredientes: producto.ingredientes ? Object.values(producto.ingredientes).flat() : []
                };
    
                if (productoFinal.id !== null) {
                    console.log(`🛠️ Producto agregado: ${JSON.stringify(productoFinal)}`);
                    productosSeleccionados.push(productoFinal);
                } else {
                    console.warn(`⚠️ Producto inválido, ID nulo: ${JSON.stringify(producto)}`);
                }
            }
        });
    
        if (productosSeleccionados.length === 0) {
            console.warn("⚠️ No hay productos válidos en `productosSeleccionados`. No se enviará el pedido.");
            alert("Debes seleccionar al menos un producto con cantidad mayor a 0.");
            return;
        }
    
        let formData = JSON.stringify({
            cliente_nombre: clienteNombre,
            productos: productosSeleccionados
        });
    
        console.log("🔹 JSON que se enviará a `savePedido`:", formData);
    
        fetch("/savePedido/", {
            method: "POST",
            mode: "same-origin",
            credentials: "include",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log("🔹 Respuesta de `savePedido`:", data);
            if (data.success) {
                alert("Pedido guardado correctamente.");
                window.location.reload();
            } else {
                alert("Error al guardar el pedido: " + data.error);
            }
        })
        .catch(error => {
            console.error("❌ Error al enviar pedido:", error);
            alert("Ocurrió un error al enviar el pedido. Revisa la consola.");
        });
    }
});
