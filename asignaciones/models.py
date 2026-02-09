from django.db import models
from django.core.exceptions import ValidationError


class Asignacion(models.Model):
    proyecto = models.ForeignKey('proyectos.Proyecto', on_delete=models.CASCADE)
    aprendiz = models.ForeignKey('aprendices.Aprendiz', on_delete=models.CASCADE)
    instructor = models.ForeignKey('instructores.Instructor', on_delete=models.SET_NULL, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['proyecto', 'aprendiz'],
                condition=models.Q(activo=True),
                name='unique_active_assignment_per_project'
            )
        ]

    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })

    def __str__(self):
        return f"{self.proyecto.codigo} - {self.aprendiz.nombres}"
