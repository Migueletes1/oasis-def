from django.db import models

class Auditoria(models.Model):
    accion = models.CharField(max_length=50)
    tabla = models.CharField(max_length=50)
    registro_id = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.accion} en {self.tabla} ({self.fecha})"
