import re

from django import forms
from django.core.exceptions import ValidationError

from .models import ProyectoGrado, Carrera


class ProyectoGradoAdminForm(forms.ModelForm):
    """Admin form for creating/editing ProyectoGrado with enhanced UX."""

    class Meta:
        model = ProyectoGrado
        fields = [
            'titulo', 'descripcion', 'resumen', 'carrera', 'autor',
            'email_autor', 'ficha', 'instructor_avalador',
            'thumbnail', 'imagen_url', 'enlace_repositorio', 'enlace_demo',
            'anio', 'tags', 'herramientas_usadas', 'version_actual', 'estado',
            'destacado',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Titulo del proyecto de grado',
                'data-tooltip': 'Titulo oficial del proyecto (min. 5 caracteres)',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'admin-input', 'rows': 5,
                'placeholder': 'Descripcion completa del proyecto...',
            }),
            'resumen': forms.Textarea(attrs={
                'class': 'admin-input', 'rows': 3, 'maxlength': 500,
                'placeholder': 'Resumen ejecutivo (max 500 caracteres)',
                'data-tooltip': 'Breve resumen que aparecera en la tarjeta del explorador',
            }),
            'carrera': forms.HiddenInput(attrs={'id': 'id_carrera'}),
            'autor': forms.TextInput(attrs={
                'class': 'admin-input', 'id': 'id_autor',
                'placeholder': 'Nombre del autor o buscar aprendiz...',
                'autocomplete': 'off',
                'data-tooltip': 'Escribe para buscar aprendices registrados',
            }),
            'email_autor': forms.EmailInput(attrs={
                'class': 'admin-input', 'id': 'id_email_autor',
                'placeholder': 'email@sena.edu.co',
            }),
            'ficha': forms.TextInput(attrs={
                'class': 'admin-input', 'id': 'id_ficha',
                'placeholder': 'Ej: 2845673',
                'data-tooltip': 'Numero de ficha SENA del aprendiz',
            }),
            'instructor_avalador': forms.Select(attrs={
                'class': 'admin-input',
            }),
            'thumbnail': forms.ClearableFileInput(attrs={
                'class': 'hidden', 'id': 'id_thumbnail',
                'accept': 'image/*',
            }),
            'imagen_url': forms.URLInput(attrs={
                'class': 'admin-input',
                'placeholder': 'https://ejemplo.com/imagen.jpg',
            }),
            'enlace_repositorio': forms.URLInput(attrs={
                'class': 'admin-input',
                'placeholder': 'https://github.com/usuario/proyecto',
                'data-tooltip': 'Link al repositorio de codigo (GitHub, GitLab, etc.)',
            }),
            'enlace_demo': forms.URLInput(attrs={
                'class': 'admin-input',
                'placeholder': 'https://demo.ejemplo.com',
                'data-tooltip': 'Link a una demo funcional del proyecto',
            }),
            'anio': forms.NumberInput(attrs={
                'class': 'admin-input', 'min': 2020, 'max': 2035,
            }),
            'tags': forms.CheckboxSelectMultiple(),
            'herramientas_usadas': forms.TextInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Python, React, Figma (separado por comas)',
                'data-tooltip': 'Lista de herramientas y tecnologias usadas',
            }),
            'version_actual': forms.Select(attrs={'class': 'admin-input'}),
            'estado': forms.Select(attrs={'class': 'admin-input'}),
        }

    def clean_titulo(self):
        val = self.cleaned_data.get('titulo', '').strip()
        if len(val) < 5:
            raise ValidationError('El titulo debe tener al menos 5 caracteres.')
        return val

    def clean_descripcion(self):
        val = self.cleaned_data.get('descripcion', '').strip()
        if len(val) < 20:
            raise ValidationError('La descripcion debe tener al menos 20 caracteres.')
        return val

    def clean_resumen(self):
        val = self.cleaned_data.get('resumen', '').strip()
        if val and len(val) > 500:
            raise ValidationError('El resumen no puede exceder 500 caracteres.')
        return val


class CarreraAdminForm(forms.ModelForm):
    """Admin form for Carrera CRUD."""

    class Meta:
        model = Carrera
        fields = ['clave', 'nombre', 'cluster', 'icono', 'descripcion', 'activa', 'orden']
        widgets = {
            'clave': forms.TextInput(attrs={
                'class': 'admin-input',
                'placeholder': 'software, contabilidad...',
                'data-tooltip': 'Clave unica en minusculas sin espacios (ej: ciencia_datos)',
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Desarrollo de Software',
            }),
            'cluster': forms.Select(attrs={'class': 'admin-input'}),
            'icono': forms.TextInput(attrs={
                'class': 'admin-input', 'id': 'id_icono',
                'placeholder': 'fa-code',
                'data-tooltip': 'Clase FontAwesome 6 (ej: fa-code, fa-robot)',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'admin-input', 'rows': 3,
                'placeholder': 'Descripcion de la carrera...',
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'admin-input', 'min': 0,
            }),
        }

    def clean_clave(self):
        val = self.cleaned_data.get('clave', '').strip().lower()
        if not re.match(r'^[a-z][a-z0-9_]*$', val):
            raise ValidationError('La clave debe ser minusculas, sin espacios (ej: ciencia_datos).')
        return val
