from rest_framework import serializers
from .models import Transaction
from backend.models import Usuario, ItemPedido, Producto, Categoria
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
    



class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario(
            email=validated_data['email'],
            username=validated_data['username'],
            nombre=validated_data['nombre'],
            apellido=validated_data['apellido']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class ItemPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = ['id', 'producto', 'precio', 'cantidad', 'pedido']
