from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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
