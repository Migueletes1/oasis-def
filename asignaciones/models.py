from django.db import models

class Asignacion(models.Model):
    proyecto = models.ForeignKey('proyectos.Proyecto', on_delete=models.CASCADE)
    aprendiz = models.ForeignKey('aprendices.Aprendiz', on_delete=models.CASCADE)
    instructor = models.ForeignKey('instructores.Instructor', on_delete=models.SET_NULL, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.proyecto.codigo} - {self.aprendiz.nombres}"
