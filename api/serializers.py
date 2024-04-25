from rest_framework import serializers
from .models import Transaction
from backend.models import Usuario, Producto, Categoria,Carrito, ItemPedido, Pedido
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
        fields = ['id', 'nombre', 'apellido', 'username', 'email', 'password', 'direccion', 'region', 'comuna', 'telefono']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario(
            email=validated_data['email'],
            username=validated_data['username'],
            nombre=validated_data['nombre'],
            apellido=validated_data['apellido'],
            direccion=validated_data['direccion'],
            region=validated_data['region'],
            comuna=validated_data['comuna'],
            telefono=validated_data['telefono'],
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

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']


class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer()

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen']


class ItemPedidoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()

    class Meta:
        model = ItemPedido
        fields = ['producto', 'precio', 'cantidad']


class PedidoSerializer(serializers.ModelSerializer):
    items = ItemPedidoSerializer(many=True)

    class Meta:
        model = Pedido
        fields = ['id', 'fecha_creacion', 'actualizado_en', 'estado', 'completado','items']


class CarritoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()  # Usar UsuarioSerializer para serializar el usuario
    items = ItemPedidoSerializer(many=True)  # Indica que puede haber varios items

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'creado_en', 'actualizado_en', 'items']  # Incluye 'usuario' en los campos

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        usuario_data = validated_data.pop('usuario')  # Obtener datos del usuario
        usuario_id = usuario_data.get('id')  # Obtener el ID del usuario
        carrito = Carrito.objects.create(usuario_id=usuario_id, **validated_data)  # Asociar el carrito al usuario mediante su ID
        for item_data in items_data:
            ItemPedido.objects.create(carrito=carrito, **item_data)
        return carrito

