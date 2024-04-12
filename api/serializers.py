from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['buy_order', 'session_id', 'amount', 'status', 'response_code', 'transaction_date', 'last_update']
        read_only_fields = ['status', 'response_code', 'transaction_date', 'last_update']

    def validate_amount(self, value):
        """
        Check that the amount is a positive number.
        """
        if value <= 0:
            raise serializers.ValidationError("The amount must be greater than zero.")
        return value
