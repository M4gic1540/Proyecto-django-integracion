from rest_framework import serializers
from .models import Usuario, Producto, Categoria, Pedido, ItemPedido

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'nombre', 'apellido', 'estado', 'credito', 'imagen']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), source='categoria', write_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'stock', 'categoria', 'categoria_id', 'imagen']

class PedidoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), source='usuario', write_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'usuario_id', 'fecha_creacion', 'actualizado_en', 'estado', 'completado']

class ItemPedidoSerializer(serializers.ModelSerializer):
    pedido = PedidoSerializer(read_only=True)
    pedido_id = serializers.PrimaryKeyRelatedField(queryset=Pedido.objects.all(), source='pedido', write_only=True)
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all(), source='producto', write_only=True)

    class Meta:
        model = ItemPedido
        fields = ['id', 'pedido', 'pedido_id', 'producto', 'producto_id', 'precio', 'cantidad']
