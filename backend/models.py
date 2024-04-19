from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

class UsuarioManager(BaseUserManager):
    def _create_user(self, username, email, nombre, apellido, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un correo electrónico")
        email = self.normalize_email(email)
        usuario = self.model(
            username=username,
            email=email,
            nombre=nombre,
            apellido=apellido,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario
    
    def create_user(self, username, email, nombre, apellido, password=None, **extra_fields):
        return self._create_user(
            username,
            email,
            nombre,
            apellido,
            password,
            False,
            False,
            **extra_fields
        )

    def create_superuser(self, username, email, nombre, apellido, password=None, **extra_fields):
        return self._create_user(
            username,
            email,
            nombre,
            apellido,
            password,
            True,
            True,
            **extra_fields
        )

class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('Nombre de usuario', unique=True, max_length=100)
    email = models.EmailField('Correo electrónico', unique=True, max_length=250)
    nombre = models.CharField('Nombre completo', max_length=200)
    apellido = models.CharField('Apellidos', max_length=200)
    estado = models.CharField('Estado', max_length=50, default='DISPONIBLE')
    credito = models.FloatField('Crédito', default=0)
    imagen = models.ImageField('Imagen de perfil', upload_to='perfil', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nombre', 'apellido']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.username})'

    def get_full_name(self):
        return f'{self.nombre} {self.apellido}'

    def get_short_name(self):
        return self.nombre


# Modelo de Categoría para productos
class Categoria(models.Model):
    nombre = models.CharField('Nombre de la categoría', max_length=100)
    descripcion = models.TextField('Descripción', blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre

# Modelo de Producto
class Producto(models.Model):
    nombre = models.CharField('Nombre del producto', max_length=255)
    descripcion = models.TextField('Descripción', blank=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    stock = models.IntegerField('Stock disponible')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    imagen = models.ImageField('Imagen del producto', upload_to='productos/', blank=True, null=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('producto_detalle', kwargs={'pk': self.pk})

# Modelo de Pedido
class Pedido(models.Model):
    ESTADO_CHOICES = (
        ('en_carrito', 'En Carrito'),
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    actualizado_en = models.DateTimeField('Última actualización', auto_now=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='en_carrito')
    completado = models.BooleanField('Pedido completado', default=False)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido {self.id} - {self.usuario}'

    def get_total(self):
        total = sum(item.get_cost() for item in self.items.all())
        return total

# Modelo de Item de Pedido
class ItemPedido(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT, related_name='item_pedidos')
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    cantidad = models.IntegerField('Cantidad', default=1)

    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre} - {self.pedido}'

    def clean(self):
        """ Verifica que la cantidad no exceda el stock disponible. """
        if self.cantidad > self.producto.stock:
            raise ValidationError(f'No hay suficiente stock para {self.producto.nombre}. Disponible: {self.producto.stock}, solicitado: {self.cantidad}.')

    @transaction.atomic
    def save(self, *args, **kwargs):
        """ Actualiza el stock del producto al guardar el item del pedido dentro de una transacción atómica. """
        if self.pk is None:  # Nuevo objeto, reducir el stock
            self.producto.stock -= self.cantidad
            self.producto.save()
        else:  # Objeto existente, verificar la diferencia en la cantidad
            original = ItemPedido.objects.get(pk=self.pk)
            if self.cantidad != original.cantidad:
                # Ajustar el stock basado en la diferencia
                self.producto.stock += original.cantidad - self.cantidad
                self.producto.save()
        super().save(*args, **kwargs)
        self.producto.refresh_from_db()  # Recargar el estado del producto para reflejar cambios recientes en el stock

    @property
    def get_cost(self):
        """ Retorna el costo total del item de pedido. """
        return self.precio * self.cantidad
    
    
    
class Carrito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carritos')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Carrito de {self.usuario.username}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())