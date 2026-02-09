from django.db import models


class Seguimiento(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]

    asignacion = models.ForeignKey(
        'asignaciones.Asignacion',
        on_delete=models.CASCADE,
        related_name='seguimientos',
    )
    fecha = models.DateField(auto_now_add=True)
    observaciones = models.TextField()
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES)

    def __str__(self):
        return f"Seguimiento {self.id} - {self.fecha}"
