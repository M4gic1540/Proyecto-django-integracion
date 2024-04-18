from django.db import models

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('initiated', 'Initiated'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    buy_order = models.CharField(max_length=64, unique=True)
    session_id = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='initiated')
    response_code = models.IntegerField(null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    token_ws = models.CharField(max_length=128, unique=True, null=True, blank=True)

    def __str__(self):
        return f'Transaction {self.buy_order} - {self.status}'
