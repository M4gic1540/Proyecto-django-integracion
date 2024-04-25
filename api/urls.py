from django.urls import path
from .views import CreateTransaction, TransactionDetail, TransactionList,CarritoAPIView, payment_success, listar_Usuario_api, crear_usuario_api
from . import views

urlpatterns = [
    path('transactions/', TransactionList.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', TransactionDetail.as_view(), name='transaction-detail'),
    path('create-transaction/', CreateTransaction.as_view(), name='create-transaction'),
    path('payment-success/', payment_success, name='payment-success'),
    path('payment-error/', payment_success, name='payment-error'),
    path('usuarios/', crear_usuario_api, name='crear_usuario'),
    path('usuarios/listar/', listar_Usuario_api, name='listar_usuarios'),
    path('categorias/', views.CategoriaList.as_view(), name='categoria-list'),
    path('categorias/<int:pk>/', views.CategoriaDetail.as_view(), name='categoria-detail'),
    path('productos/', views.ProductoList.as_view(), name='producto-list'),
    path('productos/<int:pk>/', views.ProductoDetail.as_view(), name='producto-detail'),
    path('pedidos/', views.PedidoList.as_view(), name='pedido-list'),
    path('pedidos/<int:pk>/', views.PedidoDetail.as_view(), name='pedido-detail'),
    path('carritos/', CarritoAPIView.as_view(), name='carrito-list'),
    path('carritos/<int:pk>/', views.CarritoDetail.as_view(), name='carrito-detail'),

]


