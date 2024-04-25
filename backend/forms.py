from django import forms
from .models import Usuario, ItemPedido, Producto, Categoria
from django.contrib.auth.hashers import make_password


class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Confirma contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'username',
                  'email', 'password1', 'password2','direccion', 'region', 'comuna', 'telefono']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.password = make_password(
            self.cleaned_data['password1'])  # Hash password
        if commit:
            user.save()
        return user


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio',
                  'stock', 'categoria', 'imagen']


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']


class PedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        # `precio` podría ser calculado automáticamente basado en el producto seleccionado
        fields = ['pedido', 'producto', 'cantidad']

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        producto = self.cleaned_data.get('producto')

        if not isinstance(producto, Producto):
            raise forms.ValidationError(
                "El producto debe ser un objeto de la clase 'Producto'.")

        if not isinstance(cantidad, int):
            raise forms.ValidationError("La cantidad debe ser un número.")
        if cantidad < 1:
            raise forms.ValidationError("La cantidad debe ser al menos 1.")
        if cantidad > producto.stock:
            raise forms.ValidationError("No hay suficiente stock disponible.")
        return cantidad


class CarritoAddProductoForm(forms.ModelForm):
    cantidad = forms.IntegerField(min_value=1, initial=1)
    actualizar = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

    class Meta:
        model = ItemPedido
        fields = ['cantidad', 'actualizar']