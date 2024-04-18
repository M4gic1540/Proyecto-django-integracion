from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('carrito/',views.carrito, name='carrito'),
    path('accounts/panel',views.panel, name='panel'),

]   