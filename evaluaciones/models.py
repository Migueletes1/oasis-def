from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Evaluacion(models.Model):
    asignacion = models.ForeignKey(
        'asignaciones.Asignacion',
        on_delete=models.CASCADE,
        related_name='evaluaciones',
    )
    fecha = models.DateField(auto_now_add=True)
    calificacion = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5.0)],
    )
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Evaluacion {self.id} - {self.calificacion}"
