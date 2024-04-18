from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def home (request):
    return render(request, 'home.html', {})


@login_required(login_url = 'login')
def carrito(request):
    return render(request, './carrito/carrito-compras.html', {})

def deslogear(request):
    logout(request)
    messages.success(request, 'Sesion terminada')
    return redirect('login')

@login_required(login_url = 'login')
def panel(request):
    return render(request, 'usuario/panel.html', {})



def loguear(request):
    if request.user.is_authenticated:
        return redirect('panel')
    if request.method == 'POST':
        username = request.POST['usuario']
        contraseña = request.POST['contraseña']

        user = authenticate(request, username=username, password=contraseña)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {username}')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrecto')

    context = {}
    return render(request, 'usuario/login.html', context)