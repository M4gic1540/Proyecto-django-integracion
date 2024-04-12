from django.urls import path
from .views import CreateTransaction, TransactionDetail, TransactionList

urlpatterns = [
    path('transactions/', TransactionList.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', TransactionDetail.as_view(), name='transaction-detail'),
    path('create-transaction/', CreateTransaction.as_view(), name='create-transaction'),
]
