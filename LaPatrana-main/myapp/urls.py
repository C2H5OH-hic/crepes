from django.urls import path
from . import views

urlpatterns = [
     path('', views.signin, name="signin"),
     path('administrador/', views.administrador, name="administrador"),
     path('chef/', views.chef, name="chef"),
     path('signout/', views.signout, name='signout'),
     path('createUser/', views.createUser, name='createUser'),
     path('showUsers/', views.showUsers, name="showUsers"),
     path('listUsers/', views.listUsers, name="listUsers"),
     path('listProductos/', views.listProductos, name="listProductos"),
     path('deleteUser/<int:user_id>/', views.deleteUser, name="deleteUser"),
     path('actulizarDatosUsuario/<int:user_id>/', views.actualizarDatosUsuario, name="actulizarDatosUsuario"),
     path('createProduct/', views.createProduct, name='createProduct'),
     path('savePedido/', views.savePedido, name='savePedido'),
     path('cambiar_estado_pedido/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
     path('verFacturaID/', views.verFacturaID, name='verFacturaID'),
     path('verFactura/', views.verFactura, name='verFactura'),
     path('borrarPedido/<int:pedido_id>/', views.borrarPedido, name='borrarPedido'),
     path('pedidos_publicos/', views.pedidos_publicos, name='pedidos_publicos'),
     path('tomarPedido/', views.tomarPedido, name='tomarPedido')
]
