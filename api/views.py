
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction as TransbankTransaction
from .models import Transaction
from .serializers import TransactionSerializer
from django.conf import settings
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView

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
                    return_url='http://127.0.0.1:8000/api/transactions/'
                )

                # Actualiza la transacción con la información recibida de Transbank
                transaction.status = 'completed'  # Este estado debería ajustarse según la respuesta de Transbank
                transaction.token = response['token']  # Accede al token usando corchetes ya que es un diccionario
                transaction.url = response['url']     # Accede a la URL usando corchetes
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
