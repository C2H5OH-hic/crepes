from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.core import serializers
from django.conf import settings
from .forms import ProductoForm, ProductoActividadForm, ActividadForm, ProductoIngredienteFormSet, IngredienteForm, CompraForm, DetalleCompraFormSet, ProveedorForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from datetime import datetime, date
from .models import User, Producto, Pedido, DetallePedido, Actividad, ValidacionCosto, Ingrediente, ProductoIngrediente, Insumo, Proveedor, Compra, DetalleCompra
from pathlib import Path
import uuid

def inicio(request):
    return render(request, 'inicio.html')

def signin(request):
    """
    Maneja el inicio de sesión y redirige según el tipo de usuario.
    """
    if request.user.is_authenticated:  # Si ya está logueado, redirige según el rol
        if request.user.is_cashier:
            return redirect('tomarPedido')  # Redirige al cajero
        elif request.user.is_chef:
            return redirect('chef')  # Redirige al chef
        elif request.user.is_superuser:
            return redirect('administrador')  # Redirige al administrador

    if request.method == 'GET':
        return render(request, 'index.html')  # Muestra el formulario de login
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_cashier:
                return redirect('tomarPedido')
            elif user.is_chef:
                return redirect('chef')
            elif user.is_superuser:
                return redirect('administrador')
        else:
            return render(request, 'index.html', {'error': 'Credenciales incorrectas.'})

def signout(request):
    """
    Cierra la sesión del usuario y redirige al login.
    """
    logout(request)  # Cierra la sesión
    return redirect('/')  # Redirige al login

@login_required
def administrador(request):
    """
    Vista principal para administradores.
    """
    users = User.objects.all()
    return render(request, 'administrador.html', {'users': users})


@login_required
def createUser(request):
    """
    Vista para crear un nuevo usuario.
    """
    if request.method == 'GET':
        return render(request, 'createUser.html')
    elif request.method == 'POST':
        try:
            # Tipo de usuario: Chef o Cajero
            user_type = request.POST.get("Tipo", "")
            is_cashier = user_type == 'Cajero'
            is_chef = user_type == 'Chef'

            # Crear el usuario
            user = User.objects.create_user(
                username=request.POST["username"],
                password=request.POST["password"],
                first_name=request.POST["name"],
                last_name=request.POST["lastname"],
                email=request.POST["email"]
            )
            user.is_cashier = is_cashier
            user.is_chef = is_chef
            user.save()
            return render(request, 'createUser.html', {'success': True})
        except Exception as e:
            return render(request, 'createUser.html', {'success': False, 'error': str(e)})

@login_required
def deleteUser(request, user_id):
    """
    Elimina un usuario por su ID.
    """
    try:
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return JsonResponse({'success': True, 'message': 'Usuario eliminado correctamente.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def showUsers(request):
    """
    Vista para mostrar la lista de usuarios.
    """
    users = User.objects.all()
    return render(request, 'showUsers.html', {'users': users})


@login_required
def listUsers(request):
    """
    Devuelve la lista de usuarios en un formato JSON.
    """
    if request.method == 'GET':
        users = User.objects.all()
        data = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'type': 'Cajero' if user.is_cashier else 'Chef' if user.is_chef else 'Otro',
            }
            for user in users
        ]
        return JsonResponse({'users': data}, safe=False)


@login_required
def actualizarDatosUsuario(request, user_id):
    """
    Actualiza la información del usuario.
    """
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        data = request.POST
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.username = data.get('username', user.username)
        user.is_active = data.get('is_active', user.is_active)
        user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@login_required
def chef(request):
    """
    Vista principal del chef que muestra pedidos no despachados y sus productos.
    """
    usuario = request.user
    pedidos = Pedido.objects.exclude(estado='despachado')  # Excluir pedidos despachados

    # Preparar los pedidos con sus detalles
    pedidos_context = []
    for pedido in pedidos:
        productos = DetallePedido.objects.filter(pedido=pedido)  # Obtener detalles del pedido
        productos_listos = productos.filter(estado='listo').count()
        total_productos = productos.count()
        pedidos_context.append({
            'pedido': pedido,
            'productos': productos,
            'productos_listos': productos_listos,
            'total_productos': total_productos,
        })

    return render(request, 'chef.html', {
        'usuario': usuario,
        'pedidos_context': pedidos_context,
    })


@login_required
def marcar_producto_listo(request, producto_id):
    """
    Marca un producto como listo.
    """
    detalle = get_object_or_404(DetallePedido, id=producto_id)
    detalle.estado = 'listo'
    detalle.save()
    return redirect('chef')


@login_required
def despachar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, idPedido=pedido_id)
    productos = DetallePedido.objects.filter(pedido=pedido)

    if all(producto.estado == 'listo' for producto in productos):
        pedido.estado = 'despachado'
        pedido.created_at = datetime.now()  # Actualizar fecha de creación al despachar
        pedido.save()
        print(f"Pedido {pedido.idPedido} despachado correctamente.")
    else:
        print(f"No todos los productos del pedido {pedido.idPedido} están listos.")

    return redirect('chef')

@login_required
def tomarPedido(request):
    """
    Muestra productos disponibles para crear un pedido.
    Genera un ID temporal basado en el último pedido.
    """
    # Obtener el último pedido registrado
    ultimo_pedido = Pedido.objects.last()
    id_temporal = ultimo_pedido.idPedido + 1 if ultimo_pedido else 1

    # Obtener productos disponibles
    productos = Producto.objects.filter(disponible=True)

    return render(request, 'tomarPedido.html', {
        'id_temporal': id_temporal,
        'productos': productos
    })

@login_required
def savePedido(request):
    """
    Guarda un pedido con los productos seleccionados.
    """
    if request.method == 'POST':
        try:
            productos_seleccionados = request.POST.getlist('productos_seleccionados[]')
            cantidades = {key.split('_')[1]: value for key, value in request.POST.items() if key.startswith('cantidad_')}
            notas = {key.split('_')[1]: value for key, value in request.POST.items() if key.startswith('notas_')}
            cliente_nombre = request.POST.get('cliente_nombre', 'Cliente')
            idCajero = request.user.id

            pedido = Pedido.objects.create(cliente_nombre=cliente_nombre, idCajero_id=idCajero)

            for producto_id in productos_seleccionados:
                cantidad = int(cantidades.get(producto_id, 0))
                nota = notas.get(producto_id, '')
                if cantidad > 0:
                    producto = Producto.objects.get(idProducto=producto_id)
                    DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad, nota=nota)

            return redirect('tomarPedido')
        except Exception as e:
            return render(request, 'tomarPedido.html', {'error': True, 'error_message': str(e)})
    else:
        return render(request, 'tomarPedido.html')


@login_required
def borrarPedido(request, pedido_id):
    """
    Elimina un pedido.
    """
    pedido = get_object_or_404(Pedido, idPedido=pedido_id)
    pedido.delete()
    return redirect('chef')

@login_required
def crear_producto(request):
    """
    Vista para crear un producto y asignar ingredientes al mismo tiempo.
    """
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()  # Guarda el producto
            # Procesar el formset después de guardar el producto
            formset = ProductoIngredienteFormSet(request.POST, instance=producto)
            if formset.is_valid():
                formset.save()  # Guarda los ingredientes vinculados al producto
                return redirect('productos')  # Redirige a la lista de productos
        else:
            # Si el formulario no es válido, vuelve a mostrar los errores
            formset = ProductoIngredienteFormSet(request.POST)
    else:
        form = ProductoForm()
        formset = ProductoIngredienteFormSet()

    return render(request, 'crear_producto.html', {'form': form, 'formset': formset})

@login_required
def crear_producto(request):
    """
    Vista para crear un producto sin asociarlo a ingredientes.
    """
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Solo guarda el producto, sin asociar ingredientes
            return redirect('productos')  # Redirige a la lista de productos
    else:
        form = ProductoForm()

    return render(request, 'crear_producto.html', {'form': form})


@login_required
def eliminarProductos(request):
    """
    Muestra la lista de productos con imágenes en una plantilla para eliminarlos.
    """
    productos = Producto.objects.all()  # Recupera todos los productos
    return render(request, 'eliminarProductos.html', {'productos': productos})

@login_required
def deleteProduct(request, product_id):
    """
    Elimina un producto por su ID.
    """
    try:
        producto = get_object_or_404(Producto, idProducto=product_id)
        producto.delete()  # Elimina el producto
        return redirect('eliminarProductos')  # Redirige de nuevo a la lista
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def cambiar_estado_pedido(request, pedido_id):
    """
    Cambia el estado de un pedido.
    """
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, idPedido=pedido_id)
        nuevo_estado = request.POST.get('estado')
        estados_validos = ['pendiente', 'aceptado', 'listo', 'despachado']

        if nuevo_estado in estados_validos:
            pedido.estado = nuevo_estado
            pedido.save()
            return JsonResponse({'success': True, 'nuevo_estado': nuevo_estado})

        return JsonResponse({'success': False, 'error': 'Estado no válido'}, status=400)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def listProductos(request):
    """
    Devuelve la lista de productos en formato JSON.
    """
    if request.method == 'GET':
        productos = Producto.objects.all()
        data = [
            {
                'id': producto.idProducto,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': str(producto.precio),
                'disponible': producto.disponible,
            }
            for producto in productos
        ]
        return JsonResponse({'productos': data}, safe=False)

@login_required
def generar_caja_diaria(request):
    fecha_actual = date.today()
    pedidos = Pedido.objects.filter(created_at__date=fecha_actual, estado='despachado')

    total_caja = 0
    detalles_pedidos = []

    for pedido in pedidos:
        productos = DetallePedido.objects.filter(pedido=pedido)
        total_pedido = sum(detalle.cantidad * detalle.producto.precio for detalle in productos)
        total_caja += total_pedido

        detalles_pedidos.append({
            'id': pedido.idPedido,
            'cliente': pedido.cliente_nombre,
            'hora': pedido.created_at.strftime('%H:%M:%S'),
            'productos': [
                f"{detalle.producto.nombre} (x{detalle.cantidad})"
                for detalle in productos
            ],
            'total_pedido': total_pedido
        })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="caja_diaria_{fecha_actual}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle(f"Caja Diaria - {fecha_actual}")

    ancho, alto = letter
    y = alto - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, y, f"Caja Diaria - {fecha_actual}")
    y -= 30

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Total de la Caja: ${total_caja:.2f}")
    y -= 40

    # Configurar tabla
    data = [["ID Pedido", "Cliente", "Hora", "Productos", "Total"]]
    for detalle in detalles_pedidos:
        data.append([
            detalle['id'],
            detalle['cliente'],
            detalle['hora'],
            "\n".join(detalle['productos']),
            f"${detalle['total_pedido']:.2f}"
        ])

    table = Table(data, colWidths=[50, 100, 80, 250, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(pdf, 50, y - len(data) * 20)
    table.drawOn(pdf, 50, y - len(data) * 20)

    pdf.save()
    return response

@login_required
def caja_diaria(request):
    from datetime import date

    # Filtrar pedidos despachados de hoy
    pedidos = Pedido.objects.filter(created_at__date=date.today(), estado='despachado')

    if not pedidos.exists():
        print("No se encontraron pedidos despachados para hoy.")

    # Calcular datos para la plantilla
    datos_pedidos = []
    total_caja = 0

    for pedido in pedidos:
        productos = DetallePedido.objects.filter(pedido=pedido)
        if not productos.exists():
            print(f"No se encontraron productos para el pedido {pedido.idPedido}.")
        
        total_pedido = sum(detalle.cantidad * detalle.producto.precio for detalle in productos)
        total_caja += total_pedido

        datos_pedidos.append({
            'pedido': pedido,
            'productos': productos,
            'total_pedido': total_pedido
        })

    print(f"Total de pedidos procesados: {len(datos_pedidos)}")
    print(f"Total de la caja diaria: {total_caja}")

    return render(request, 'caja_diaria.html', {
        'datos_pedidos': datos_pedidos,
        'total_caja': total_caja
    })

@login_required
def pedidos_chef_ajax(request):
    pedidos = Pedido.objects.exclude(estado='despachado')  # Ajusta según la lógica que necesites
    data = []

    for pedido in pedidos:
        detalles = DetallePedido.objects.filter(pedido=pedido)
        productos = [
            {
                "nombre": detalle.producto.nombre,
                "cantidad": detalle.cantidad,
                "nota": detalle.nota  # Asegúrate de que este atributo exista
            }
            for detalle in detalles
        ]

        data.append({
            "id": pedido.idPedido,
            "cliente_nombre": pedido.cliente_nombre,
            "productos": productos,
            "estado": pedido.get_estado_display(),
        })

    return JsonResponse({"pedidos": data, "csrf_token": request.META.get('CSRF_COOKIE', '')})

@login_required
def productos(request):
    """
    Vista general para la gestión de productos. Muestra la pantalla de opciones.
    """
    return render(request, 'productos.html')  # Renderiza la pantalla de opciones

def pedidos_publicos_view(request):
    """
    Renderiza la plantilla de pedidos públicos.
    """
    return render(request, 'pedidos_publicos.html')

def pedidos_publicos_ajax(request):

    pedidos = Pedido.objects.filter(estado__in=['pendiente', 'aceptado', 'listo']).order_by('estado', 'idPedido')
    data = []

    for pedido in pedidos:
        detalles = DetallePedido.objects.filter(pedido=pedido)
        productos = [
            {
                "nombre": detalle.producto.nombre,
                "cantidad": detalle.cantidad,
                "nota": getattr(detalle, "nota", "Sin nota"),
            }
            for detalle in detalles
        ]

        data.append({
            "id": pedido.idPedido,
            "cliente_nombre": pedido.cliente_nombre,
            "productos": productos,
            "estado": pedido.get_estado_display(),
        })

    return JsonResponse({"pedidos": data})


def lista_productos(request):
    productos = Producto.objects.filter(disponible=True)
    return render(request, 'lista_productos.html', {'productos': productos})

# ---------------------------------------------
# ANÁLISIS Y RECOMENDACIONES
# ---------------------------------------------

@login_required
def recomendaciones_view(request):
    productos = Producto.objects.all()
    recomendaciones = []

    for producto in productos:
        margen = producto.margen_beneficio()
        if margen < 500:  # Umbral de margen bajo
            recomendaciones.append(f"Incrementar precio o reducir costos de {producto.nombre}.")

        validaciones = ValidacionCosto.objects.filter(producto=producto)
        if any(v.discrepancia > 0 for v in validaciones):
            recomendaciones.append(f"Revisar actividad o consumo real para {producto.nombre}.")

    return render(request, 'recomendaciones.html', {'recomendaciones': recomendaciones})


@login_required
def costos_unitarios(request):
    productos = Producto.objects.all()
    resultados = []

    for producto in productos:
        costo_unitario = producto.calcular_costo_unitario()
        margen = producto.margen_beneficio()
        resultados.append({
            'nombre': producto.nombre,
            'costo_unitario': costo_unitario,
            'precio': producto.precio,
            'margen': margen,
        })

    return render(request, 'costos_unitarios.html', {'resultados': resultados})


# ---------------------------------------------
# ACTIVIDADES
# ---------------------------------------------

@login_required
def lista_actividades(request):
    actividades = Actividad.objects.all()
    return render(request, 'lista_actividades.html', {'actividades': actividades})


@login_required
def crear_actividad(request):
    if request.method == 'POST':
        form = ActividadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_actividades')
    else:
        form = ActividadForm()

    return render(request, 'crear_actividad.html', {'form': form})


@login_required
def asignar_actividad(request, actividad_id):
    """
    Vista para asignar una actividad a productos.
    """
    actividad = get_object_or_404(Actividad, id=actividad_id)
    if request.method == 'POST':
        form = ProductoActividadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_actividades')
    else:
        form = ProductoActividadForm(initial={'actividad': actividad})

    return render(request, 'asignar_actividad.html', {'form': form, 'actividad': actividad})


# ---------------------------------------------
# INGREDIENTES
# ---------------------------------------------

@login_required
def lista_ingredientes(request):
    ingredientes = Ingrediente.objects.all()
    return render(request, 'lista_ingredientes.html', {'ingredientes': ingredientes})


@login_required
def crear_ingrediente(request):
    producto_id = request.GET.get('producto_id')  # Recuperar el ID del producto, si existe
    if request.method == 'POST':
        form = IngredienteForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirigir según el contexto
            if producto_id:
                return redirect('vincular_ingredientes', producto_id=producto_id)
            return redirect('lista_ingredientes')  # Redirige a la lista general de ingredientes
    else:
        form = IngredienteForm()

    return render(request, 'crear_ingrediente.html', {'form': form, 'producto_id': producto_id})


@login_required
def vincular_ingredientes(request, producto_id):
    producto = get_object_or_404(Producto, idProducto=producto_id)
    ingredientes_disponibles = Ingrediente.objects.exclude(productoingrediente__producto=producto)

    return render(request, 'vincular_ingredientes.html', {
        'producto': producto,
        'ingredientes_disponibles': ingredientes_disponibles
    })


@login_required
def agregar_ingrediente(request, producto_id):
    producto = get_object_or_404(Producto, idProducto=producto_id)

    if request.method == 'POST':
        ingrediente_id = request.POST.get('ingrediente_id')
        cantidad_requerida = request.POST.get('cantidad_requerida')

        if ingrediente_id and cantidad_requerida:
            ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id)
            ProductoIngrediente.objects.create(
                producto=producto,
                ingrediente=ingrediente,
                cantidad_requerida=cantidad_requerida
            )

    return redirect('vincular_ingredientes', producto_id=producto.idProducto)

@login_required
def eliminar_ingrediente(request, producto_id, ingrediente_id):
    """
    Elimina un ingrediente vinculado a un producto específico.
    """
    vinculo = get_object_or_404(ProductoIngrediente, producto_id=producto_id, ingrediente_id=ingrediente_id)
    if request.method == 'POST':
        vinculo.delete()
    return redirect('vincular_ingredientes', producto_id=producto_id)

@login_required
def eliminar_ingrediente_general(request, ingrediente_id):
    """
    Elimina un ingrediente de la lista general de ingredientes.
    """
    ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id)
    if request.method == 'POST':
        ingrediente.delete()
        return redirect('lista_ingredientes')
    return redirect('lista_ingredientes')  # Redirige si no es POST

@login_required
def gestion(request):
    """
    Página principal de gestión de ingredientes y actividades.
    """
    return render(request, 'gestion.html')

@login_required
def gestion_costos(request):
    """
    Lista productos con sus costos unitarios, precios de venta y márgenes.
    """
    productos = Producto.objects.all()
    resultados = []

    for producto in productos:
        costo_unitario = producto.calcular_costo_unitario()
        margen = producto.margen_beneficio()
        resultados.append({
            'producto': producto,
            'costo_unitario': costo_unitario,
            'margen': margen,
        })

    return render(request, 'gestion_costos.html', {'resultados': resultados})

@login_required
def registrar_compra(request):
    """
    Vista para registrar una compra con opción de ingredientes o insumos.
    """
    if request.method == 'POST':
        form = CompraForm(request.POST)
        formset = DetalleCompraFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            compra = form.save(commit=False)
            compra.usuario = request.user
            compra.save()
            formset.instance = compra

            for detalle_form in formset.cleaned_data:
                tipo = detalle_form.get('tipo')
                ingrediente = detalle_form.get('ingrediente') if tipo == 'ingrediente' else None
                nombre_insumo = detalle_form.get('nombre_insumo') if tipo == 'insumo' else None
                cantidad = detalle_form.get('cantidad')
                precio_unitario = detalle_form.get('precio_unitario')

                DetalleCompra.objects.create(
                    compra=compra,
                    ingrediente=ingrediente,
                    nombre_insumo=nombre_insumo,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )
            return redirect('lista_compras')

    else:
        form = CompraForm()
        formset = DetalleCompraFormSet(queryset=DetalleCompra.objects.none())

    return render(request, 'registrar_compra.html', {'form': form, 'formset': formset})


@login_required
def lista_proveedores(request):
    """
    Lista de proveedores existentes.
    """
    proveedores = Proveedor.objects.all()
    return render(request, 'lista_proveedores.html', {'proveedores': proveedores})


@login_required
def registrar_proveedor(request):
    """
    Registrar un nuevo proveedor.
    """
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()

    return render(request, 'registrar_proveedor.html', {'form': form})


@login_required
def eliminar_proveedor(request, proveedor_id):
    """
    Eliminar un proveedor existente.
    """
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.delete()
    return redirect('lista_proveedores')

@login_required
def lista_compras(request):
    """
    Lista de compras con detalles procesados para manejar ingredientes e insumos.
    """
    compras = Compra.objects.prefetch_related('detalles')

    for compra in compras:
        compra.total = sum(
            detalle.cantidad * detalle.precio_unitario for detalle in compra.detalles.all()
        )

        # Procesar cada detalle para priorizar el nombre del insumo
        for detalle in compra.detalles.all():
            detalle.nombre_completo = (
                detalle.nombre_insumo if detalle.nombre_insumo else
                detalle.ingrediente.nombre if detalle.ingrediente else
                "Sin Nombre"
            )

    return render(request, 'lista_compras.html', {'compras': compras})

@login_required
def analisis_costos_unitarios(request):
    """
    Vista que muestra un análisis detallado de los costos unitarios de cada producto.
    """
    productos = Producto.objects.all()
    analisis = [producto.analizar_costos() for producto in productos]

    return render(request, 'analisis_costos.html', {'analisis': analisis})
