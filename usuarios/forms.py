import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import Usuario


class LoginForm(AuthenticationForm):
    """Formulario de login con estilos Tailwind."""

    username = forms.CharField(
        label='Usuario o Email',
        widget=forms.TextInput(attrs={
            'class': 'auth-input',
            'placeholder': 'correo@institucional.edu.co',
            'autocomplete': 'username',
        }),
    )
    password = forms.CharField(
        label='Contrasena',
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        }),
    )


class EmpresaRegistroForm(forms.ModelForm):
    """
    Formulario de solicitud de registro para Empresas.
    Al registrarse, is_active = False hasta aprobacion del admin.
    """

    password1 = forms.CharField(
        label='Contrasena',
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        }),
        help_text='Minimo 10 caracteres, al menos 1 mayuscula, 1 numero y 1 caracter especial.',
    )
    password2 = forms.CharField(
        label='Confirmar contrasena',
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        }),
    )

    class Meta:
        model = Usuario
        fields = [
            'nombre_empresa', 'nit_empresa', 'email',
            'first_name', 'last_name', 'telefono', 'motivo_registro',
        ]
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={
                'class': 'auth-input', 'placeholder': 'Nombre legal de la empresa',
            }),
            'nit_empresa': forms.TextInput(attrs={
                'class': 'auth-input', 'placeholder': '900.123.456-7',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'auth-input', 'placeholder': 'contacto@empresa.com',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'auth-input', 'placeholder': 'Nombre del representante',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'auth-input', 'placeholder': 'Apellido del representante',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'auth-input', 'placeholder': '+573001234567',
            }),
            'motivo_registro': forms.Textarea(attrs={
                'class': 'auth-input', 'rows': 3,
                'placeholder': 'Describa brevemente por que desea acceder al repositorio de talento...',
            }),
        }
        labels = {
            'nombre_empresa': 'Razon Social',
            'nit_empresa': 'NIT',
            'email': 'Email corporativo',
            'first_name': 'Nombre del representante',
            'last_name': 'Apellido del representante',
            'telefono': 'Telefono',
            'motivo_registro': 'Motivo de registro',
        }

    def clean_nombre_empresa(self):
        val = self.cleaned_data.get('nombre_empresa', '').strip()
        if not val:
            raise ValidationError('El nombre de la empresa es obligatorio.')
        if len(val) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        return val

    def clean_nit_empresa(self):
        val = self.cleaned_data.get('nit_empresa', '').strip()
        if not val:
            raise ValidationError('El NIT es obligatorio.')
        if Usuario.objects.filter(nit_empresa=val).exists():
            raise ValidationError('Ya existe una empresa registrada con este NIT.')
        return val

    def clean_email(self):
        val = self.cleaned_data.get('email', '').strip().lower()
        if not val:
            raise ValidationError('El email es obligatorio.')
        if Usuario.objects.filter(email=val).exists():
            raise ValidationError('Ya existe una cuenta con este email.')
        return val

    def clean_motivo_registro(self):
        val = self.cleaned_data.get('motivo_registro', '').strip()
        if not val:
            raise ValidationError('Debe indicar el motivo de su registro.')
        if len(val) < 20:
            raise ValidationError('El motivo debe tener al menos 20 caracteres.')
        return val

    def clean_password1(self):
        pw = self.cleaned_data.get('password1', '')
        if len(pw) < 10:
            raise ValidationError('La contrasena debe tener al menos 10 caracteres.')
        if not re.search(r'[A-Z]', pw):
            raise ValidationError('Debe contener al menos una letra mayuscula.')
        if not re.search(r'\d', pw):
            raise ValidationError('Debe contener al menos un numero.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', pw):
            raise ValidationError('Debe contener al menos un caracter especial.')
        return pw

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get('password1')
        pw2 = cleaned.get('password2')
        if pw1 and pw2 and pw1 != pw2:
            self.add_error('password2', 'Las contrasenas no coinciden.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.rol = Usuario.Rol.EMPRESA
        user.is_active = False  # Requiere aprobacion del admin
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
