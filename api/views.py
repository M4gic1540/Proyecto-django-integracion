
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction as TransbankTransaction
from .models import Transaction
from .serializers import TransactionSerializer, ProductoSerializer, UsuarioSerializer,CategoriaSerializer, ProductoSerializer, PedidoSerializer, CarritoSerializer
from django.conf import settings
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework import generics
from backend.models import Producto, Usuario,Categoria, Producto, Pedido, Carrito
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.shortcuts import render

class CreateTransaction(APIView):
    def post(self, request):
        # Deserializa la información entrante y la valida
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            # Crea la instancia del modelo Transaction con estado 'initiated'
            transaction = serializer.save(status='initiated')

            try:
                # Crea la instancia de TransbankTransaction usando la configuración de Django settings
                tx = TransbankTransaction(settings.WEBPAY_OPTIONS)
                # Realiza el llamado a Transbank para iniciar la transacción
                response = tx.create(
                    buy_order=transaction.buy_order,
                    session_id=transaction.session_id,
                    amount=transaction.amount,
                    return_url='http://127.0.0.1:8000/api/payment-success/'
                )

                # Actualiza la transacción con la información recibida de Transbank
                # Este estado debería ajustarse según la respuesta de Transbank
                transaction.status = 'completed'
                # Accede al token usando corchetes ya que es un diccionario
                transaction.token = response['token']
                # Accede a la URL usando corchetes
                transaction.url = response['url']
                transaction.save()

                # Devuelve la URL y token para redirección del lado del cliente
                return Response({
                    'url': transaction.url,
                    'token': transaction.token
                }, status=status.HTTP_200_OK)
            except TransbankError as e:
                # Maneja errores específicos de Transbank y actualiza el estado
                transaction.response_code = e.response_code
                transaction.last_update = e.last_update
                transaction.status = 'failed'
                transaction.save()
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                # Maneja otros errores posibles y actualiza el estado
                transaction.status = 'error'
                transaction.save()
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Devuelve errores de validación
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionList(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class ProductoList(APIView):
    """
    List all products, or create a new product.
    """

    def get(self, request, format=None):
        productos = Producto.objects.all()
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
def crear_usuario_api(request):
    if request.method == 'POST':
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'detail': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def listar_Usuario_api(request):
    if request.method == 'GET':
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)
    else:
        return Response({'detail': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def payment_success(request):
    token_ws = request.GET.get('token_ws')
    if token_ws:
        # Busca la transacción usando session_id
        try:
            transaction = Transaction.objects.get(token_ws=token_ws)
            
            if transaction.status == 'completed':
                # Si la transacción está completada, muestra una página de éxito.
                return render(request, 'carrito/success.html', {'transaction': transaction})
            else:
                # Si la transacción no está completada, muestra un mensaje apropiado.
                return render(request, 'carrito/payment_error.html', {'message': 'La transacción no ha sido completada.'})
        except Transaction.DoesNotExist:
            # Si no se encuentra ninguna transacción con ese session_id
            return render(request, 'carrito/payment_error.html', {'message': 'No se encontró la transacción.'})
    else:
        # Si no se proporciona token
        return HttpResponse("Token de transacción no proporcionado.", status=400)


# Asegúrate de tener las plantillas payment_success.html y payment_error.html para manejar estas respuestas.

class CategoriaList(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class CategoriaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProductoList(generics.ListCreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ProductoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class PedidoList(generics.ListCreateAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

class PedidoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

class CarritoList(generics.ListCreateAPIView):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer

class CarritoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer


class CarritoAPIView(APIView):
    def get(self, request):
        carritos = Carrito.objects.all()
        serializer = CarritoSerializer(carritos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CarritoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
