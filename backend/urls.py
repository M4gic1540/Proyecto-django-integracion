from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('carrito/',views.carrito, name='carrito'),
    path('accounts/login/',views.loguear, name='login'),
    path('accounts/agregar/', views.agregarUsuario, name='agregarUsuario'),
    path('accounts/registrar/', views.registro, name='registroUsuarios'),
    path('accounts/logout/', views.deslogear, name='logout'),  # Usa el nuevo nombre de la función
    path('accounts/panel',views.panel, name='panel'),
    path('home/', views.home, name='home'),
        # Rutas para Productos
    path('productos/listar/', views.listar_productos, name='listar_productos'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),

    # Rutas para Categorías
    path('categorias/listar/', views.listar_categorias, name='listar_categorias'),
    path('categorias/agregar/', views.agregar_categoria, name='agregar_categoria'),
    path('categorias/editar/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),

    # Rutas para Items de Pedido
    path('items_pedido/listar/', views.listar_items_pedido, name='listar_items_pedido'),
    path('items_pedido/agregar/', views.agregar_item_pedido, name='agregar_item_pedido'),
    path('items_pedido/editar/<int:item_id>/', views.editar_item_pedido, name='editar_item_pedido'),
]