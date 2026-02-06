from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import Auditoria
import json
from django.core.serializers.json import DjangoJSONEncoder

# Import models to track
from proyectos.models import Proyecto
from empresas.models import Empresa
from aprendices.models import Aprendiz
from instructores.models import Instructor
from asignaciones.models import Asignacion
from seguimientos.models import Seguimiento
from evaluaciones.models import Evaluacion

MODELS_TO_TRACK = [Proyecto, Empresa, Aprendiz, Instructor, Asignacion, Seguimiento, Evaluacion]

def get_model_data(instance):
    try:
        data = model_to_dict(instance)
        # Convert date/decimal objects to string for storage
        return json.dumps(data, cls=DjangoJSONEncoder)
    except Exception:
        return str(instance)

@receiver(post_save)
def auditoria_post_save(sender, instance, created, **kwargs):
    if sender not in MODELS_TO_TRACK:
        return

    accion = 'CREATE' if created else 'UPDATE'
    tabla = sender._meta.model_name
    registro_id = instance.id
    
    valor_nuevo = get_model_data(instance)
    
    Auditoria.objects.create(
        accion=accion,
        tabla=tabla,
        registro_id=registro_id,
        valor_nuevo=valor_nuevo,
        valor_anterior=None # Simplification: capturing only new state on update for now
    )

@receiver(post_delete)
def auditoria_post_delete(sender, instance, **kwargs):
    if sender not in MODELS_TO_TRACK:
        return

    accion = 'DELETE'
    tabla = sender._meta.model_name
    registro_id = instance.id
    
    valor_anterior = get_model_data(instance)
    
    Auditoria.objects.create(
        accion=accion,
        tabla=tabla,
        registro_id=registro_id,
        valor_anterior=valor_anterior
    )
