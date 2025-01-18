from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from .utils import enviar_informe_caja_diaria


urlpatterns = [
    # Página principal
    path('', views.inicio, name="inicio"),  

    # Inicio de sesión y usuarios
    path('login/', views.signin, name="signin"),
    path('signout/', views.signout, name='signout'),
    path('createUser/', views.createUser, name='createUser'),
    path('showUsers/', views.showUsers, name="showUsers"),
    path('listUsers/', views.listUsers, name="listUsers"),
    path('deleteUser/<int:user_id>/', views.deleteUser, name="deleteUser"),
    path('actualizarDatosUsuario/<int:user_id>/', views.actualizarDatosUsuario, name="actualizarDatosUsuario"),


    # Administrador
    path('administrador/', views.administrador, name="administrador"),  
    
    # Vista para el Chef
    path('chef/', views.chef, name="chef"),
    path('chef/pedidos_ajax/', views.pedidos_chef_ajax, name='pedidos_chef_ajax'),

    # Productos
    path('productos/', views.productos, name='productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:producto_id>/ingredientes/', views.vincular_ingredientes, name='vincular_ingredientes'),
    path('productos/<int:producto_id>/ingredientes/agregar/', views.agregar_ingrediente, name='agregar_ingrediente'),
    path('productos/<int:idProducto>/', views.detalle_producto, name='detalle_producto'),
    path('productos/<int:producto_id>/ingredientes/<int:ingrediente_id>/eliminar/', views.eliminar_ingrediente, name='eliminar_ingrediente'),
    path('deleteProduct/<int:product_id>/', views.deleteProduct, name='deleteProduct'),  # Eliminar un producto
    path('listProductos/', views.listProductos, name="listProductos"),  # Mostrar productos disponibles

    # Gestión de Ingredientes
    path('gestion/ingredientes/', views.lista_ingredientes, name='lista_ingredientes'),
    path('gestion/ingredientes/seleccionar/', views.seleccionar_producto, name='seleccionar_producto'),

    # Crear Ingredientes
    path('ingredientes/crear/', views.crear_ingrediente, name='crear_ingrediente'),

    # Pedidos
    path('savePedido/', views.savePedido, name='savePedido'),
    path('tomarPedido/', views.tomarPedido, name='tomarPedido'),
    path('borrarPedido/<int:pedido_id>/', views.borrarPedido, name='borrarPedido'),
    path('cambiar_estado_pedido/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('producto/<int:producto_id>/listo/', views.marcar_producto_listo, name='marcar_producto_listo'),
    path('pedido/<int:pedido_id>/despachar/', views.despachar_pedido, name='despachar_pedido'),
    path('pedidos_publicos/', views.pedidos_publicos_view, name='pedidos_publicos'),
    path('pedidos_publicos_ajax/', views.pedidos_publicos_ajax, name='pedidos_publicos_ajax'),

    # Caja diaria
    path('cajaDiaria/', views.generar_caja_diaria, name='cajaDiaria'),

    # Actividades y costos
    path('actividades/crear/', views.crear_actividad, name="crear_actividad"),
    path('actividades/asignar/<int:actividad_id>/', views.asignar_actividad, name='asignar_actividad'),
    path('costos/unitarios/', views.costos_unitarios, name="costos_unitarios"),
    path('analisis_costos/', views.analisis_costos_unitarios, name='analisis_costos_unitarios'),

    # Compras y proveedores
    path('compras/', views.lista_compras, name='lista_compras'),
    path('compras/registrar/', views.registrar_compra, name='registrar_compra'),
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/registrar/', views.registrar_proveedor, name='registrar_proveedor'),
    path('proveedores/eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),

    # Gestión
    path('gestion/', views.gestion, name='gestion'),
    path('gestion/costos/', views.gestion_costos, name='gestion_costos'),
    path('gestion/productos/', views.gestion_productos, name='gestion_productos'),
    path('gestion/actividades/', views.lista_actividades, name='lista_actividades'),
    path('gestion/ingredientes/<int:ingrediente_id>/eliminar/', views.eliminar_ingrediente_general, name='eliminar_ingrediente_general'),

    # Lista de productos públicos
    path('productos-publicos/', views.lista_productos, name='lista_productos_publicos'),

    # Gestión de costos
    path('gestion/costos/', views.gestion_costos, name='gestion_costos'),

    # Ruta de eliminación general de productos
    path('productos/<int:product_id>/eliminar/', views.deleteProduct, name='deleteProduct'),

    # notificaciones
    path('notificaciones-margenes/', views.notificaciones_margenes, name='notificaciones_margenes'),

    # Enviar correo automatico  
    path('api/ingredientes/', views.obtener_ingredientes, name='obtener_ingredientes'),

    path('graficos-costos-ingredientes/', views.graficos_costos_ingredientes, name='graficos_costos_ingredientes'),

    # Inventario
    path('inventario/', views.lista_inventario, name='lista_inventario'),

    # Categorías
    path('categorias/', views.gestionar_categorias, name='gestionar_categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:categoria_id>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:categoria_id>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
