from django.db import models

class Proyecto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='proyectos')
    
    def __str__(self):
        return self.nombre
