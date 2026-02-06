from django.db import models

class Evaluacion(models.Model):
    asignacion = models.ForeignKey('asignaciones.Asignacion', on_delete=models.CASCADE, related_name='evaluaciones')
    fecha = models.DateField(auto_now_add=True)
    calificacion = models.DecimalField(max_digits=4, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Evaluación {self.id} - {self.calificacion}"
