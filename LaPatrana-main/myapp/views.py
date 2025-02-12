from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError, transaction
from decimal import Decimal
from django.db.models import Sum, F
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from .forms import ProductoForm, ProductoActividadForm, ActividadForm, ProductoIngredienteFormSet, IngredienteForm, CompraForm, DetalleCompraFormSet, ProveedorForm, CategoriaForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib import colors
from datetime import datetime, date
from .models import User, Producto, Pedido, DetallePedido, Actividad, ValidacionCosto, Ingrediente, ProductoIngrediente, Insumo, Proveedor, Compra, DetalleCompra, Categoria, DetallePedidoIngrediente
from pathlib import Path
import uuid
import json


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
    if not request.user.is_superuser:
        return redirect('inicio')  # Redirige a la plantilla de inicio si no es administrador

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
    Elimina un usuario por su ID y redirige a la lista de usuarios.
    """
    try:
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return redirect('showUsers')  # Redirige a la página de lista de usuarios
    except Exception as e:
        # En caso de error, puedes redirigir a una página de error o mostrar un mensaje.
        return render(request, 'error.html', {'message': str(e)})

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
    Actualiza la información de un usuario.
    """
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Procesar el formulario
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.username = request.POST.get('username', user.username)
        user.is_cashier = request.POST.get('Tipo') == 'Cajero'
        user.is_chef = request.POST.get('Tipo') == 'Chef'
        user.save()

        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('showUsers')  # Redirige a la lista de usuarios

    # Renderizar el formulario con los datos actuales del usuario
    return render(request, 'updateUser.html', {'user': user})

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
    Vista para tomar pedidos. Carga la lista de productos disponibles,
    sus ingredientes adicionales, y prepara un ID temporal para el pedido.
    """

    # Obtener el último pedido para generar un ID temporal
    ultimo_pedido = Pedido.objects.last()
    id_temporal = (ultimo_pedido.idPedido + 1) if ultimo_pedido else 1

    # Filtrar solo los productos disponibles
    productos = Producto.objects.filter(disponible=True).prefetch_related('productoingrediente_set__ingrediente')

    # Construir el contexto de productos
    productos_context = []
    for producto in productos:
        # Evitar enviar productos sin nombre o sin precio
        if not producto.nombre or producto.precio is None:
            print(f"⚠️ Producto inválido detectado y omitido: {producto}")
            continue

        # Obtener los ingredientes adicionales asociados al producto
        ingredientes_adicionales = ProductoIngrediente.objects.filter(
            producto=producto,
            ingrediente__categoria='adicional'
        ).values(
            'ingrediente__id',
            'ingrediente__nombre'
        )

        productos_context.append({
            "idProducto": producto.idProducto,
            "nombre": producto.nombre,
            "precio": float(producto.precio),
            "categoria": producto.categoria.nombre if producto.categoria else "Sin categoría",
            "imgProducto": producto.imgProducto.url if producto.imgProducto else '/static/img/default.jpg',
            "ingredientes_adicionales": list(ingredientes_adicionales),
        })

    print("🔹 Productos enviados a `tomarpedido.html`:", json.dumps(productos_context, indent=2))

    # Renderizar la plantilla
    return render(request, 'tomarPedido.html', {
        'productos_context': json.dumps(productos_context),  # Serializar productos como JSON
        'id_temporal': id_temporal,
    })

@csrf_exempt
@login_required
def savePedido(request):
    if request.method == 'POST':
        try:
            print("🔹 request.body recibido en Django:", request.body)

            # 1. Leer los datos JSON correctamente
            if request.content_type == "application/json":
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except json.JSONDecodeError:
                    print("❌ Error al decodificar JSON")
                    return JsonResponse({'success': False, 'error': 'Error al procesar JSON'}, status=400)
            else:
                print("⚠️ `Content-Type` no es JSON, intentando leer `request.POST`")
                data = request.POST.dict()
                productos = []
                data["productos"] = productos

            print(f"🔹 JSON procesado en Django: {data}")

            # 2. Crear el pedido
            cliente_nombre = data.get('cliente_nombre', 'Cliente')
            productos = data.get('productos', [])
            idCajero = request.user.id

            with transaction.atomic():
                pedido = Pedido.objects.create(cliente_nombre=cliente_nombre, idCajero_id=idCajero)
                print(f"✅ Pedido creado: Pedido {pedido.idPedido}")

                detalles_registrados = False

                for item in productos:
                    producto_id = item.get('id')
                    cantidad = item.get('cantidad', 0)
                    nota = item.get('nota', '')

                    if not producto_id or cantidad <= 0:
                        continue

                    try:
                        producto = Producto.objects.get(idProducto=producto_id)
                        detalle = DetallePedido.objects.create(
                            pedido=pedido,
                            producto=producto,
                            cantidad=cantidad,
                            estado="pendiente",
                            nota=nota
                        )
                        detalles_registrados = True

                        # 📌 Verificación de los ingredientes recibidos
                        ingredientes_por_unidad = item.get("ingredientesPorUnidad", {})

                        # **Si `ingredientesPorUnidad` no existe, distribuimos manualmente los `ingredientes`**
                        if not ingredientes_por_unidad:
                            print(f"⚠️ No se encontraron `ingredientesPorUnidad` para {producto.nombre}, asignando manualmente")

                            ingredientes_globales = item.get("ingredientes", [])
                            ingredientes_por_unidad = {str(i): [] for i in range(cantidad)}

                            # **Distribuir ingredientes sin perder combinaciones**
                            distribucion = [[] for _ in range(cantidad)]
                            for i, ing in enumerate(ingredientes_globales):
                                distribucion[i % cantidad].append(ing)

                            # Asignamos la distribución final a cada unidad
                            for unidad_idx in range(cantidad):
                                ingredientes_por_unidad[str(unidad_idx)] = distribucion[unidad_idx]

                        print(f"🔍 Ingredientes asignados por unidad para {producto.nombre}: {ingredientes_por_unidad}")

                        # **Asignar los ingredientes correctamente a cada unidad**
                        for unidad_idx in range(cantidad):
                            ingredientes_actuales = ingredientes_por_unidad.get(str(unidad_idx), [])

                            if not ingredientes_actuales:
                                print(f"⚠️ Unidad {unidad_idx} de {producto.nombre} no tiene ingredientes explícitos.")

                            for ingrediente in ingredientes_actuales:
                                try:
                                    ingrediente_id = int(ingrediente["id"])
                                    ingrediente_obj = Ingrediente.objects.get(id=ingrediente_id)

                                    ingrediente_obj.frecuencia_uso += 1
                                    ingrediente_obj.save()

                                    # Evita duplicados con `get_or_create`
                                    dp_ing, created = DetallePedidoIngrediente.objects.get_or_create(
                                        detalle_pedido=detalle,
                                        ingrediente=ingrediente_obj,
                                        unidad=unidad_idx
                                    )
                                    if created:
                                        dp_ing.cantidadIngrediente = 1
                                    else:
                                        dp_ing.cantidadIngrediente += 1
                                    dp_ing.save()

                                except Ingrediente.DoesNotExist:
                                    print(f"⚠️ Ingrediente con ID {ingrediente_id} no encontrado. Omitiendo...")

                        print(f"✅ Detalle registrado con ingredientes para {detalle}")

                    except Producto.DoesNotExist:
                        print(f"❌ Producto con ID {producto_id} no encontrado. Omitiendo...")

                if not detalles_registrados:
                    print(f"❌ No se registraron detalles. Eliminando pedido {pedido.idPedido}...")
                    pedido.delete()
                    return JsonResponse(
                        {'success': False, 'error': 'No se pudo guardar el pedido porque no hay productos válidos.'},
                        status=400
                    )

                print(f"✅ Pedido {pedido.idPedido} registrado correctamente.")
                return JsonResponse({'success': True, 'message': 'Pedido guardado correctamente.'})

        except Exception as e:
            print(f"❌ Error en `savePedido`: {e}")
            return JsonResponse({'success': False, 'error': 'Error al guardar el pedido.'}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


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
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gestion_productos')
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
    if request.method == 'POST':
        try:
            producto = get_object_or_404(Producto, idProducto=product_id)
            producto.delete()
            return JsonResponse({'success': True}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

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
    compras = Compra.objects.prefetch_related('detalles').filter(fecha__date=fecha_actual)

    total_caja = 0
    detalles_pedidos = []
    total_compras = 0
    detalles_compras = []

    # Procesar pedidos
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

    # Procesar compras
    for compra in compras:
        total_compra = sum(detalle.cantidad * detalle.precio_unitario for detalle in compra.detalles.all())
        total_compras += total_compra

        detalles = [
            f"{detalle.nombre_insumo if detalle.nombre_insumo else detalle.ingrediente.nombre} - {detalle.cantidad} x ${detalle.precio_unitario:.2f}"
            for detalle in compra.detalles.all()
        ]

        detalles_compras.append({
            'id': compra.id,
            'proveedor': compra.proveedor.nombre,
            'fecha': compra.fecha.strftime('%H:%M:%S'),
            'detalles': detalles,
            'total_compra': total_compra
        })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="caja_diaria_{fecha_actual}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    ancho, alto = letter
    y = alto - 50

    # Encabezado con logo y título
    logo_path = Path(settings.BASE_DIR).resolve() / 'myapp' / 'static' / 'img' / 'logocrepes.jpg'
    if logo_path.exists():
        pdf.drawImage(str(logo_path), 50, alto - 100, width=100, height=50)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(200, alto - 70, "Reporte Diario - Caja")
    pdf.line(50, alto - 120, ancho - 50, alto - 120)
    y = alto - 130

    # Totales generales
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Total de Ingresos: ${total_caja:.2f}")
    pdf.drawString(50, y - 20, f"Total de Compras: ${total_compras:.2f}")
    pdf.drawString(50, y - 40, f"Balance Neto: ${total_caja - total_compras:.2f}")
    pdf.line(50, y - 50, ancho - 50, y - 50)
    y -= 70

    # Tablas
    data_pedidos = [["ID Pedido", "Cliente", "Hora", "Productos", "Total"]] + [
        [detalle['id'], detalle['cliente'], detalle['hora'], "\n".join(detalle['productos']), f"${detalle['total_pedido']:.2f}"]
        for detalle in detalles_pedidos
    ]
    data_compras = [["ID Compra", "Proveedor", "Hora", "Detalles", "Total"]] + [
        [
            detalle['id'],
            detalle['proveedor'],
            detalle['fecha'],
            "\n".join(detalle['detalles']),
            f"${detalle['total_compra']:.2f}"
        ]
        for detalle in detalles_compras
    ]

    # Dibujar tablas
    table_pedidos = Table(data_pedidos, colWidths=[50, 100, 80, 250, 70])
    table_pedidos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    table_pedidos.wrapOn(pdf, 50, y - len(data_pedidos) * 20)
    table_pedidos.drawOn(pdf, 50, y - len(data_pedidos) * 20)

    y -= len(data_pedidos) * 20 + 40
    table_compras = Table(data_compras, colWidths=[50, 100, 80, 250, 70])
    table_compras.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    table_compras.wrapOn(pdf, 50, y - len(data_compras) * 20)
    table_compras.drawOn(pdf, 50, y - len(data_compras) * 20)

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
    # Obtenemos los pedidos (por ejemplo, los que no estén despachados)
    pedidos = Pedido.objects.exclude(estado='despachado')
    data = []

    for pedido in pedidos:
        detalles = DetallePedido.objects.filter(pedido=pedido).select_related('producto')
        productos = []

        for detalle in detalles:
            # Aquí armamos un diccionario de la forma: {unidad_idx: [{nombre, cantidadIngrediente}, ...], ...}
            ingredientes_por_unidad = {}

            # Incluimos "cantidadIngrediente" en el values()
            qs_ingredientes = DetallePedidoIngrediente.objects.filter(detalle_pedido=detalle).values(
                "unidad", "ingrediente__nombre", "cantidadIngrediente"
            )

            for ing in qs_ingredientes:
                unidad = ing["unidad"]
                if unidad not in ingredientes_por_unidad:
                    ingredientes_por_unidad[unidad] = []
                ingredientes_por_unidad[unidad].append({
                    "nombre": ing["ingrediente__nombre"],
                    "cantidadIngrediente": ing["cantidadIngrediente"],
                })

            productos.append({
                "nombre": detalle.producto.nombre,
                "cantidad": detalle.cantidad,
                "nota": detalle.nota,
                "ingredientes_por_unidad": ingredientes_por_unidad
            })

        data.append({
            "id": pedido.idPedido,  # O la key que uses
            "cliente_nombre": pedido.cliente_nombre,
            "productos": productos,
            "estado": pedido.get_estado_display(),  # Pendiente, Aceptado, etc.
        })

    # Retornamos un JSON con todos los pedidos y el csrf_token si deseas
    return JsonResponse({
        "pedidos": data,
        "csrf_token": request.META.get('CSRF_COOKIE', '')  # Si lo necesitas
    })

@login_required
def productos(request):
    categoria_id = request.GET.get('categoria_id')
    if categoria_id:
        productos = Producto.objects.filter(categoria_id=categoria_id)
    else:
        productos = Producto.objects.all()

    categorias = Categoria.objects.all()
    return render(request, 'productos.html', {'productos': productos, 'categorias': categorias})

@csrf_exempt
def pedidos_publicos_view(request):
    """
    Renderiza la plantilla de pedidos públicos.
    """
    return render(request, 'pedidos_publicos.html')

@csrf_exempt
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
    # Productos organizados por categoría utilizando el campo relacionado 'categoria__nombre'
    productos_simples = Producto.objects.filter(categoria__nombre='simple', disponible=True)
    productos_dobles = Producto.objects.filter(categoria__nombre='doble', disponible=True)
    productos_salados = Producto.objects.filter(categoria__nombre='salado', disponible=True)

    # Retornamos todos los productos disponibles al contexto
    productos = Producto.objects.filter(disponible=True)

    return render(request, 'lista_productos.html', {
        'productos': productos,
        'productos_simples': productos_simples,
        'productos_dobles': productos_dobles,
        'productos_salados': productos_salados,
    })


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
    """
    Vista para mostrar los costos unitarios de los productos.
    """
    productos = Producto.objects.all()
    resultados = [
        {
            'nombre': producto.nombre,
            'costo_unitario': producto.calcular_costo_unitario(),
            'precio': producto.precio,
            'margen': producto.margen_beneficio(),
        }
        for producto in productos
    ]

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
    productos = Producto.objects.all()
    ingredientes = Ingrediente.objects.all()
    producto_id = request.GET.get('producto_id')  # Extraer producto_id de los parámetros GET

    if producto_id:
        try:
            producto_id = int(producto_id)  # Asegurar que sea un entero válido
        except ValueError:
            producto_id = None

    return render(request, 'lista_ingredientes.html', {
        'productos': productos,
        'ingredientes': ingredientes,
        'producto_id': producto_id,
    })

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

from django.contrib import messages
from django.db import IntegrityError

@login_required
def vincular_ingredientes(request, producto_id):
    producto = get_object_or_404(Producto, idProducto=producto_id)
    ingredientes_disponibles = Ingrediente.objects.exclude(productoingrediente__producto=producto)

    if request.method == 'POST':
        ingrediente_id = request.POST.get('ingrediente_id')
        cantidad = request.POST.get('cantidad_requerida')

        if ingrediente_id and cantidad:
            ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id)
            try:
                ProductoIngrediente.objects.create(
                    producto=producto,
                    ingrediente=ingrediente,
                    cantidad_requerida=cantidad
                )
                # Mensaje de éxito con etiqueta
                messages.success(request, f"Ingrediente '{ingrediente.nombre}' vinculado con éxito.", extra_tags="vincular_ingredientes")
            except IntegrityError:
                messages.error(request, f"El ingrediente '{ingrediente.nombre}' ya está vinculado.", extra_tags="vincular_ingredientes")
        else:
            # Mensaje de error con etiqueta
            messages.error(request, "Debes seleccionar un ingrediente y una cantidad válida.", extra_tags="vincular_ingredientes")

    return render(request, 'vincular_ingredientes.html', {
        'producto': producto,
        'ingredientes_disponibles': ingredientes_disponibles,
    })


@login_required
def agregar_ingrediente(request, producto_id):
    producto = get_object_or_404(Producto, idProducto=producto_id)

    if request.method == 'POST':
        ingrediente_id = request.POST.get('ingrediente_id')
        cantidad_requerida = request.POST.get('cantidad_requerida')

        if ingrediente_id and cantidad_requerida:
            try:
                cantidad_requerida = float(cantidad_requerida)
                ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id)

                # Intentar crear la relación
                ProductoIngrediente.objects.create(
                    producto=producto,
                    ingrediente=ingrediente,
                    cantidad_requerida=cantidad_requerida
                )
                messages.success(request, f"Ingrediente '{ingrediente.nombre}' agregado correctamente.")
            except IntegrityError:
                messages.warning(request, f"El ingrediente '{ingrediente.nombre}' ya está vinculado al producto.")
            except ValueError:
                messages.error(request, "La cantidad requerida debe ser un número válido.")
        else:
            messages.error(request, "Faltan datos para agregar el ingrediente.")

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
    if request.method == 'POST':
        print("Datos POST recibidos:", request.POST)  # Depuración

        form = CompraForm(request.POST)
        formset = DetalleCompraFormSet(request.POST, queryset=DetalleCompra.objects.none())

        if form.is_valid() and formset.is_valid():
            compra = form.save()
            print("Compra registrada:", compra)  # Depuración

            detalles = formset.save(commit=False)
            for detalle in detalles:
                detalle.compra = compra
                detalle.save()
                print("Detalle registrado:", detalle)  # Depuración

            messages.success(request, "Compra registrada con éxito.")
            return redirect('lista_compras')
        else:
            print("Errores en el formulario principal:", form.errors)
            print("Errores en el formset:", formset.errors)

        messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        form = CompraForm()
        formset = DetalleCompraFormSet(queryset=DetalleCompra.objects.none())

    # Determinar la URL de retorno según el tipo de usuario
    if request.user.is_chef:
        volver_url = 'chef'
    elif request.user.is_cashier:
        volver_url = 'tomarPedido'
    else:
        volver_url = 'administrador'  # Caso por defecto

    ingredientes = Ingrediente.objects.all()
    return render(request, 'registrar_compra.html', {
        'form': form,
        'formset': formset,
        'ingredientes': ingredientes,
        'volver_url': volver_url,  # Pasar al contexto
    })


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

    # 🔹 Obtener datos de frecuencia de selección de ingredientes
    ingredientes_frecuencia = Ingrediente.objects.all().values_list('nombre', 'frecuencia_uso', 'costo_por_unidad')
    total_frecuencia = sum(i[1] for i in ingredientes_frecuencia)

    analisis = []

    for producto in productos:
        # 🔹 Costo total de los ingredientes usados en el producto
        costo_ingredientes = producto.costo_ingredientes()
        costo_actividades = producto.costo_actividades()

        # 🔹 Cálculo del costo ponderado de ingredientes seleccionados
        if total_frecuencia > 0:
            costo_ponderado_ingredientes = sum(
                i[2] * Decimal(i[1]) / Decimal(total_frecuencia) for i in ingredientes_frecuencia
            )
        else:
            costo_ponderado_ingredientes = Decimal(0)  # 🔹 Si no hay datos, asumimos 0

        # 🔹 Costo Unitario Total
        costo_unitario = costo_ingredientes + costo_actividades + costo_ponderado_ingredientes
        costo_unitario_iva = costo_unitario * Decimal(1.19)  # 🔹 Convertimos el IVA a Decimal

        # 🔹 Precio fijo de venta
        precio_venta = producto.precio

        # 🔹 Margen de beneficio
        margen_beneficio = precio_venta - costo_unitario
        margen_beneficio_iva = precio_venta - costo_unitario_iva

        analisis.append({
            'nombre': producto.nombre,
            'costo_ingredientes': costo_ingredientes,
            'costo_actividades': costo_actividades,
            'costo_ponderado_ingredientes': costo_ponderado_ingredientes,
            'costo_unitario': costo_unitario,
            'costo_unitario_iva': costo_unitario_iva,
            'precio_venta': precio_venta,
            'margen_beneficio': margen_beneficio,
            'margen_beneficio_iva': margen_beneficio_iva,
        })

    return render(request, 'analisis_costos.html', {'analisis': analisis})

#Gestión productos
@login_required
def gestion_productos(request):
    productos = Producto.objects.all()
    return render(request, 'gestion_productos.html', {'productos': productos})

@login_required
def detalle_producto(request, idProducto):
    producto = get_object_or_404(Producto, idProducto=idProducto)
    return render(request, 'detalle_producto.html', {'producto': producto})

@login_required
def seleccionar_producto(request):
    productos = Producto.objects.all()
    return render(request, 'seleccionar_producto.html', {'productos': productos})

@login_required
def notificaciones_margenes(request):
    productos = Producto.objects.all()
    margen_umbral = 500  # Define el margen mínimo
    notificaciones = [
        f"El margen de {producto.nombre} es muy bajo: ${producto.margen_beneficio():.2f}"
        for producto in productos if producto.margen_beneficio() < margen_umbral
    ]
    return JsonResponse({"notificaciones": notificaciones})

@login_required
def graficos_costos_ingredientes(request):
    ingredientes = Ingrediente.objects.prefetch_related('historial_costos').all()
    data = {
        "ingredientes": [
            {
                "nombre": ingrediente.nombre,
                "fechas": [historial['fecha'] for historial in ingrediente.historial_costos.values("fecha", "costo_por_unidad")],
                "costos": [float(historial['costo_por_unidad']) for historial in ingrediente.historial_costos.values("fecha", "costo_por_unidad")],
            }
            for ingrediente in ingredientes if ingrediente.historial_costos.exists()
        ]
    }
    return JsonResponse(data)

def actualizar_costo(self, cantidad_comprada, precio_unitario):
    nuevo_stock = self.stock_actual + cantidad_comprada
    if nuevo_stock > 0:
        nuevo_costo = ((self.stock_actual * self.costo_por_unidad) + 
                       (cantidad_comprada * precio_unitario)) / nuevo_stock
    else:
        nuevo_costo = 0
    self.costo_por_unidad = nuevo_costo
    self.stock_actual = nuevo_stock
    self.save()

    # Registra el historial del costo
    HistorialCostoIngrediente.objects.create(
        ingrediente=self,
        costo_por_unidad=nuevo_costo
    )

@login_required
def obtener_ingredientes(request):
    """
    Devuelve los ingredientes registrados en formato JSON.
    """
    ingredientes = Ingrediente.objects.all().values('id', 'nombre', 'categoria')
    return JsonResponse(list(ingredientes), safe=False)

@login_required
def lista_inventario(request):
    ingredientes = Ingrediente.objects.all()
    insumos = Insumo.objects.all()
    return render(request, 'lista_inventario.html', {
        'ingredientes': ingredientes,
        'insumos': insumos
    })

@login_required
def gestionar_categorias(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = CategoriaForm()

    categorias = Categoria.objects.all()
    return render(request, 'gestionar_categorias.html', {'form': form, 'categorias': categorias})


@login_required
def crear_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        if nombre:
            Categoria.objects.create(nombre=nombre, descripcion=descripcion)
            return redirect('gestionar_categorias')
    return render(request, 'crear_categoria.html')

@login_required
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        categoria.nombre = request.POST.get('nombre')
        categoria.descripcion = request.POST.get('descripcion')
        categoria.save()
        return redirect('gestionar_categorias')
    return render(request, 'editar_categoria.html', {'categoria': categoria})

@login_required
def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    categoria.delete()
    return redirect('gestionar_categorias')
