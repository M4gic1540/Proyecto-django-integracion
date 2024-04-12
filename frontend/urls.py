from django.urls import path
from api.views import CreateTransaction
from . import views

urlpatterns = [
    path('create-transaction/', CreateTransaction.as_view(), name='create-transaction'),
    path('carrito/',views.carrito, name='carrito'),
]