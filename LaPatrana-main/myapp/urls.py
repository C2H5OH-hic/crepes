from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name="inicio"),  # Ahora esta es la raíz del dominio    

    # Página de inicio (Inicio de sesión)
    path('login/', views.signin, name="signin"),
    
    # Administrador
    path('administrador/', views.administrador, name="administrador"),
    
    # Vista para el Chef
    path('chef/', views.chef, name="chef"),
    
    # Cerrar sesión
    path('signout/', views.signout, name='signout'),
    
    # Usuarios
    path('createUser/', views.createUser, name='createUser'),
    path('showUsers/', views.showUsers, name="showUsers"),
    path('listUsers/', views.listUsers, name="listUsers"),
    path('deleteUser/<int:user_id>/', views.deleteUser, name="deleteUser"),
    path('actulizarDatosUsuario/<int:user_id>/', views.actualizarDatosUsuario, name="actulizarDatosUsuario"),
    
    # Productos
    path('productos/', views.productos, name='productos'),  # Página principal de productos
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('deleteProduct/<int:product_id>/', views.deleteProduct, name='deleteProduct'),  # Eliminar un producto
    path('listProductos/', views.listProductos, name="listProductos"),  # Mostrar productos disponibles
    
    # Pedidos
    path('savePedido/', views.savePedido, name='savePedido'),
    path('tomarPedido/', views.tomarPedido, name='tomarPedido'),
    path('borrarPedido/<int:pedido_id>/', views.borrarPedido, name='borrarPedido'),
    path('cambiar_estado_pedido/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),

    # Detalles de Productos y Pedidos
    path('producto/<int:producto_id>/listo/', views.marcar_producto_listo, name='marcar_producto_listo'),
    path('pedido/<int:pedido_id>/despachar/', views.despachar_pedido, name='despachar_pedido'),

    # Chef
    path('chef/pedidos_ajax/', views.pedidos_chef_ajax, name='pedidos_chef_ajax'),

    # Pedidos publicos
    path('pedidos_publicos/', views.pedidos_publicos_view, name='pedidos_publicos'),

    # API para AJAX (devuelve JSON con los datos)
    path('pedidos_publicos_ajax/', views.pedidos_publicos_ajax, name='pedidos_publicos_ajax'),

    # Ver caja diaria
    path('cajaDiaria/', views.generar_caja_diaria, name='cajaDiaria'),

    # Lista de productos
    path('eliminarProductos/', views.eliminarProductos, name="eliminarProductos"),  # Página para listar y eliminar productos
    path('deleteProduct/<int:product_id>/', views.deleteProduct, name="deleteProduct"),  # Acción para eliminar productos
    path('productos-publicos/', views.lista_productos, name='lista_productos_publicos'),

    # AQUI COMIENZA LA GESTIÓN DE LOS MODELOS - gestionar actividades
    path('actividades/crear/', views.crear_actividad, name="crear_actividad"),
    path('actividades/asignar/<int:actividad_id>/', views.asignar_actividad, name='asignar_actividad'),
    # costos unitarios
    path('costos/unitarios/', views.costos_unitarios, name="costos_unitarios"),
    path('recomendaciones/', views.recomendaciones_view, name="recomendaciones"),

    #Ingredientes
    path('ingredientes/crear/', views.crear_ingrediente, name='crear_ingrediente'),
    path('productos/<int:producto_id>/ingredientes/', views.vincular_ingredientes, name='vincular_ingredientes'),
    path('productos/<int:producto_id>/ingredientes/agregar/', views.agregar_ingrediente, name='agregar_ingrediente'),

    path('gestion/', views.gestion, name='gestion'),
    path('gestion/ingredientes/', views.lista_ingredientes, name='lista_ingredientes'),
    path('gestion/actividades/', views.lista_actividades, name='lista_actividades'),
    path('productos/<int:producto_id>/ingredientes/<int:ingrediente_id>/eliminar/', views.eliminar_ingrediente, name='eliminar_ingrediente'),
    path('gestion/ingredientes/<int:ingrediente_id>/eliminar/', views.eliminar_ingrediente_general, name='eliminar_ingrediente_general'),
    path('gestion/costos/', views.gestion_costos, name='gestion_costos'),

    #Registrar compras
    path('compras/registrar/', views.registrar_compra, name='registrar_compra'),

    #Proveedores
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/registrar/', views.registrar_proveedor, name='registrar_proveedor'),
    path('proveedores/eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),

    path('compras/', views.lista_compras, name='lista_compras'),  # Agrega esta línea

    #analisis costos
    path('analisis_costos/', views.analisis_costos_unitarios, name='analisis_costos_unitarios'),
]
