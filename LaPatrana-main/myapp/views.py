from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime, date
from .models import User, Producto, Pedido, DetallePedido, Factura
from django.core import serializers

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
    """
    productos = Producto.objects.filter(disponible=True)
    return render(request, 'tomarPedido.html', {'productos': productos})


@login_required
def savePedido(request):
    """
    Guarda un pedido con los productos seleccionados.
    """
    if request.method == 'POST':
        try:
            productos_seleccionados = request.POST.getlist('productos_seleccionados[]')
            cantidades = {key.split('_')[1]: value for key, value in request.POST.items() if key.startswith('cantidad_')}
            cliente_nombre = request.POST.get('cliente_nombre', 'Cliente')
            idCajero = request.user.id

            pedido = Pedido.objects.create(cliente_nombre=cliente_nombre, idCajero_id=idCajero)

            for producto_id in productos_seleccionados:
                cantidad = int(cantidades.get(producto_id, 0))
                if cantidad > 0:
                    producto = Producto.objects.get(idProducto=producto_id)
                    DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)

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
def createProduct(request):
    """
    Crea un nuevo producto basado en los datos enviados desde un formulario.
    """
    if request.method == 'GET':
        # Renderiza la plantilla con el formulario para crear productos
        return render(request, 'createProduct.html')
    elif request.method == 'POST':
        try:
            # Extraer datos del formulario
            nombre = request.POST.get("nombreProducto")
            descripcion = request.POST.get("Descripcion")
            precio = request.POST.get("Precio")
            disponible = request.POST.get("toggleDisponible", False) == "on"

            # Crear instancia de Producto
            producto = Producto(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                disponible=disponible
            )

            # Guardar la imagen en la carpeta correspondiente si se proporciona
            if 'imgProducto' in request.FILES:
                imagen = request.FILES['imgProducto']
                ruta_imagen = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'img', imagen.name)
                with open(ruta_imagen, 'wb') as f:
                    for chunk in imagen.chunks():
                        f.write(chunk)
                producto.imgProducto = os.path.join('img/', imagen.name)

            # Guardar el producto en la base de datos
            producto.save()
            return render(request, 'createProduct.html', {'success': True})
        except Exception as e:
            return render(request, 'createProduct.html', {'success': False, 'error': str(e)})


@login_required
def cambiar_estado_pedido(request, pedido_id):
    """
    Cambia el estado de un pedido.
    """
    if request.method == 'POST':
        # Recuperar el pedido por ID
        pedido = get_object_or_404(Pedido, idPedido=pedido_id)

        # Obtener el nuevo estado del formulario
        nuevo_estado = request.POST.get('estado')

        # Validar que el estado sea válido
        estados_validos = ['pendiente', 'aceptado', 'listo', 'despachado']
        if nuevo_estado in estados_validos:
            pedido.estado = nuevo_estado
            pedido.save()

        # Redirigir a la vista del chef
        return redirect('chef')
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

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

    # Obtener la fecha actual
    fecha_actual = date.today()
    pedidos = Pedido.objects.filter(created_at__date=fecha_actual, estado='despachado')

    # Calcular el total de la caja diaria
    total_caja = 0
    detalles_pedidos = []  # Para registrar cada pedido y sus productos

    for pedido in pedidos:
        productos = DetallePedido.objects.filter(pedido=pedido)
        total_pedido = sum(detalle.cantidad * detalle.producto.precio for detalle in productos)
        total_caja += total_pedido

        detalles_pedidos.append({
            'id': pedido.idPedido,
            'cliente': pedido.cliente_nombre,
            'productos': [
                {
                    'nombre': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                    'precio_unitario': detalle.producto.precio,
                    'subtotal': detalle.cantidad * detalle.producto.precio
                }
                for detalle in productos
            ],
            'total_pedido': total_pedido
        })

    # Crear el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="caja_diaria_{fecha_actual}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle(f"Caja Diaria - {fecha_actual}")

    # Configuración del documento
    ancho, alto = letter
    y = alto - 50  # Posición inicial
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, y, f"Caja Diaria - {fecha_actual}")
    y -= 30

    # Total de la caja
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Total de la Caja: ${total_caja:.2f}")
    y -= 30

    # Registro de ventas
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Detalles de las Ventas:")
    y -= 20

    pdf.setFont("Helvetica", 10)
    for detalle in detalles_pedidos:
        if y < 100:  # Salto de página si se queda sin espacio
            pdf.showPage()
            y = alto - 50
            pdf.setFont("Helvetica", 10)

        pdf.drawString(50, y, f"Pedido ID: {detalle['id']} | Cliente: {detalle['cliente']}")
        y -= 20
        pdf.drawString(70, y, "Productos:")
        y -= 20

        for producto in detalle['productos']:
            pdf.drawString(90, y, f"- {producto['nombre']} (x{producto['cantidad']}) - Unitario: ${producto['precio_unitario']:.2f} - Subtotal: ${producto['subtotal']:.2f}")
            y -= 15
            if y < 100:  # Salto de página si es necesario
                pdf.showPage()
                y = alto - 50
                pdf.setFont("Helvetica", 10)

        pdf.drawString(70, y, f"Total Pedido: ${detalle['total_pedido']:.2f}")
        y -= 30

    # Guardar el PDF
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
def verFacturaID(request, idMesa):
    pedidos = Pedido.objects.filter(mesa__numero=idMesa)
    
    if not pedidos.exists():
        # Redirigir o mostrar un mensaje si no hay pedidos
        return render(request, 'verMesas.html', {'idMesa': idMesa})
    
    user_id = request.user.id
    hora = timezone.localtime(timezone.now())
    fecha = hora.date()
    total = sum(pedido.idProducto.precio * pedido.cantidad for pedido in pedidos)
    total_quantity = sum(pedido.cantidad for pedido in pedidos)  # Calculate total quantity

    # Formatear los productos pedidos en un solo string
    cosas_pedidas = ', '.join([f"{pedido.idProducto.nombre} (Cantidad: {pedido.cantidad})" for pedido in pedidos])

    # Obtener la mesa
    mesa = Mesa.objects.get(numero=idMesa)

    # Crear y guardar la nueva factura
    factura = Factura(
        valor=total,
        hora=hora,
        fecha=fecha,
        cosasPedidas=cosas_pedidas,
        idMesero=request.user,
        mesa=mesa
    )
    factura.save()

    return render(request, 'verFacturaID.html', {
        'pedidos': pedidos,
        'user_id': user_id,
        'hora': hora,
        'idMesa': idMesa,
        'total': total,
        'total_quantity': total_quantity  
    })

@login_required
def verFactura(request):
    facturas = Factura.objects.all()
    processed_facturas = []

    for factura in facturas:
        productos = factura.cosasPedidas.split(', ')
        productos_procesados = []
        for producto in productos:
            nombre, cantidad = producto.rsplit(' (Cantidad: ', 1)
            cantidad = cantidad.rstrip(')')
            productos_procesados.append({
                'nombre': nombre,
                'cantidad': cantidad
            })
        processed_facturas.append({
            'factura': factura,
            'productos': productos_procesados
        })

    return render(request, 'verFactura.html', {'processed_facturas': processed_facturas})

def pedidos_publicos(request):
    """
    Muestra los pedidos que están pendientes o en proceso (visibles públicamente).
    """
    pedidos = Pedido.objects.filter(estado__in=['pendiente', 'listo']).order_by('estado', 'idPedido')
    return render(request, 'pedidos_publicos.html', {'pedidos': pedidos})
