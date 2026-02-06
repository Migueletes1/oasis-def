from django.db import models

class ReporteGenerado(models.Model):
    nombre = models.CharField(max_length=255)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=50)
    archivo_ruta = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.fecha_generacion})"
