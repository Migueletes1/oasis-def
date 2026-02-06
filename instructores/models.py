from django.db import models

class Instructor(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
    ]
    
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES)
    numero_documento = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    especialidad = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
