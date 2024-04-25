from rest_framework import serializers
from .models import Usuario, Producto, Categoria, Pedido, ItemPedido, Carrito, ItemCarrito

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'nombre', 'apellido', 'estado', 'credito', 'imagen', 'direccion', 'region', 'comuna', 'telefono']

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
        fields = ['id', 'fecha_creacion', 'actualizado_en', 'estado', 'completado', 'items']


class ItemCarritoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()

    class Meta:
        model = ItemCarrito
        fields = ['producto', 'precio', 'cantidad']

class CarritoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    items = ItemCarritoSerializer(many=True)

    class Meta:
        model = Carrito
        fields = ['usuario', 'creado_en', 'actualizado_en', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        carrito = Carrito.objects.create(**validated_data)
        for item_data in items_data:
            producto_data = item_data.pop('producto')
            producto, _ = Producto.objects.get_or_create(**producto_data)
            ItemCarrito.objects.create(carrito=carrito, producto=producto, **item_data)
        return carrito