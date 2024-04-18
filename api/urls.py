from django.urls import path
from .views import CreateTransaction, TransactionDetail, TransactionList, payment_success

urlpatterns = [
    path('transactions/', TransactionList.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', TransactionDetail.as_view(), name='transaction-detail'),
    path('create-transaction/', CreateTransaction.as_view(), name='create-transaction'),
    path('payment-success/', payment_success, name='payment-success'),
    path('payment-error/', payment_success, name='payment-error'),
]
