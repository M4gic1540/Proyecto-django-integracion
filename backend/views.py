from django.shortcuts import render, redirect
from requests import Response
from .forms import UserRegisterForm, ProductoForm, CategoriaForm,PedidoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Usuario, ItemPedido, Producto, Categoria, Pedido
from django.contrib.auth import authenticate, login, logout
from api.serializers import TransactionSerializer
from django.conf import settings
from transbank.webpay.webpay_plus.transaction import Transaction as TransbankTransaction
from rest_framework import status
from transbank.error.transbank_error import TransbankError
from rest_framework.decorators import api_view
import requests
# Create your views here.


def home(request):
    return render(request, 'home.html', {})


@api_view(['GET', 'POST'])
def carrito(request):
    if request.method == 'POST':
        # Deserializar la información JSON entrante
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            # Guarda la transacción con un estado inicial
            transaction = serializer.save(status='initiated')

            try:
                # Crea la instancia de TransbankTransaction usando la configuración de Django settings
                tx = TransbankTransaction(settings.WEBPAY_OPTIONS)
                response = tx.create(
                    buy_order=transaction.buy_order,
                    session_id=transaction.session_id,
                    amount=transaction.amount,
                    return_url='http://127.0.0.1:8000/api/create-transaction/'
                )

                # Actualiza la transacción con la respuesta de Transbank
                transaction.status = 'completed'
                transaction.token = response['token']
                transaction.url = response['url']
                transaction.save()

                # Devuelve la URL y el token para redirección del cliente
                return Response({
                    'url': transaction.url,
                    'token': transaction.token
                }, status=status.HTTP_200_OK)
            except TransbankError as e:
                # Maneja errores específicos de Transbank
                transaction.status = 'failed'
                transaction.response_code = e.response_code
                transaction.last_update = e.last_update
                transaction.save()
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                # Maneja otros errores
                transaction.status = 'error'
                transaction.save()
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Si la validación falla, devuelve los errores
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Manejo del método GET para mostrar el carrito de compras
        return render(request, 'carrito/carrito-compras.html')


def deslogear(request):
    logout(request)
    messages.success(request, 'Sesion terminada')
    return redirect('login')


@login_required(login_url='login')
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


def registro(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            codigo = request.POST.get('txtCodigo')
            clave1 = form.cleaned_data['password1']
            clave2 = form.cleaned_data['password2']
            if clave1 == clave2:
                user = form.save(commit=False)
                if codigo == 'SUPERUSER24':
                    user.is_superuser = True
                    user.is_staff = True
                user.set_password(clave1)
                user.save()
                messages.success(request, f"Usuario {user.username} creado")
                return redirect('login')
            else:
                messages.error(request, 'Las contraseñas deben coincidir')
    else:
        form = UserRegisterForm()
    context = {'form': form}
    return render(request, 'usuario/registro.html', context)


@login_required(login_url='login')
def agregarUsuario(request):
    if request.user.is_superuser == False:
        return redirect('panel')
    if request.method == 'POST':
        usuario = Usuario()
        clave1 = request.POST['pass1']
        clave2 = request.POST['pass2']
        tipo = request.POST['tipo_usuario']
        if clave1 == clave2:
            if tipo == 'cliente':
                usuario.is_superuser = False
                usuario.is_staff = False
            else:
                usuario.is_superuser = True
                usuario.is_staff = True
            usuario.nombre = request.POST['nombre']
            usuario.apellido = request.POST['apellido']
            usuario.username = request.POST['username']
            usuario.email = request.POST['email']
            usuario.estado = request.POST['estado']
            usuario.credito = request.POST['credito']
            usuario.set_password(clave1)
            usuario.save()
            messages.success(request, 'Muy bien usuario agregado')
        else:
            messages.error(request, 'Las contraseñas no coinciden')

    return render(request, 'usuario/crud/agregar.html', {})


def logear(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('usuario')
        password = request.POST.get('contraseña')
        user = authenticate(request, username=username, password=password)
        # Depuración para ver si la autenticación es exitosa
        print("User authenticated:", user)
        if user is not None:
            login(request, user)
            # Depuración para confirmar que el login es exitoso
            print("Login successful")
            messages.success(request, f'Bienvenido {username}')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrecto')
    return render(request, 'usuario/panel.html')


def deslogear(request):
    logout(request)  # Cierra la sesión del usuario
    messages.success(request, 'Sesión terminada')
    # Asegúrate de que 'login' sea el nombre correcto de la URL
    return redirect('login')


#@login_required(login_url='login')
#def listarUsuarios(request):
#    if request.user.is_superuser == False:
#        return redirect('panel')
#    usuarios = Usuario.objects.all()
#    context = {'usuarios': usuarios}
#    return render(request, 'usuarios/crud/listar.html', context)


# VISTAS PARA PRODUCTOS

def listar_usuarios(request):
    response = requests.get('http://localhost:8000/api/usuarios/listar/')  # Asegúrate de usar la URL correcta de tu API
    usuarios = response.json() if response.status_code == 200 else []
    return render(request, 'usuario/crud/listar_usuarios.html', {'usuarios': usuarios})


def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente.')
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/agregar_producto.html', {'form': form})


def editar_producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar_producto.html', {'form': form})


# VISTAS PARA CATEGORIAS

def listar_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'categorias/listar_categorias.html', {'categorias': categorias})


def agregar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría agregada correctamente.')
            return redirect('listar_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'categorias/agregar_categoria.html', {'form': form})


def editar_categoria(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('listar_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'categorias/editar_categoria.html', {'form': form})


# VISTAS PARA PEDIDOS


def listar_items_pedido(request):
    items = ItemPedido.objects.all()
    return render(request, 'items_pedido/listar_items.html', {'items': items})

@login_required(login_url='login')
def agregar_item_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            nuevo_pedido = Pedido()  # Suponiendo que el modelo Pedido no necesita campos obligatorios
            nuevo_pedido.save()  # Guardar el nuevo pedido para generar un id
            item_pedido = form.save(commit=False)
            item_pedido.pedido = nuevo_pedido
            item_pedido.save()
            messages.success(request, 'Item de pedido agregado correctamente.')
            return redirect('listar_items_pedido')
    else:
        form = PedidoForm()
    return render(request, 'items_pedido/agregar_item.html', {'form': form})


def editar_item_pedido(request, item_id):
    item = ItemPedido.objects.get(id=item_id)
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Item de pedido actualizado correctamente.')
            return redirect('listar_items_pedido')
    else:
        form = PedidoForm(instance=item)
    return render(request, 'items_pedido/editar_item.html', {'form': form})

