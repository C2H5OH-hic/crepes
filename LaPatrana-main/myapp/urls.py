from django.urls import path
from . import views

urlpatterns = [
    # Página de inicio (Inicio de sesión)
    path('', views.signin, name="signin"),
    
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
    path('listProductos/', views.listProductos, name="listProductos"),
    path('createProduct/', views.createProduct, name='createProduct'),
    
    # Pedidos
    path('savePedido/', views.savePedido, name='savePedido'),
    path('tomarPedido/', views.tomarPedido, name='tomarPedido'),
    path('borrarPedido/<int:pedido_id>/', views.borrarPedido, name='borrarPedido'),
    path('cambiar_estado_pedido/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('pedidos_publicos/', views.pedidos_publicos, name='pedidos_publicos'),

    # Detalles de Productos y Pedidos
    path('producto/<int:producto_id>/listo/', views.marcar_producto_listo, name='marcar_producto_listo'),
    path('pedido/<int:pedido_id>/despachar/', views.despachar_pedido, name='despachar_pedido'),

    # Ver facturas
     path('cajaDiaria/', views.generar_caja_diaria, name='cajaDiaria'),
]
