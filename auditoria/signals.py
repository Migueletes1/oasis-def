import json

from django.db.models.signals import post_save, post_delete
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

from .models import Auditoria
from proyectos.models import Proyecto
from empresas.models import Empresa
from aprendices.models import Aprendiz
from instructores.models import Instructor
from asignaciones.models import Asignacion
from seguimientos.models import Seguimiento
from evaluaciones.models import Evaluacion

MODELS_TO_TRACK = [
    Proyecto, Empresa, Aprendiz, Instructor,
    Asignacion, Seguimiento, Evaluacion,
]


def get_model_data(instance):
    try:
        data = model_to_dict(instance)
        return json.dumps(data, cls=DjangoJSONEncoder)
    except Exception:
        return str(instance)


def auditoria_post_save(sender, instance, created, **kwargs):
    accion = 'CREATE' if created else 'UPDATE'
    Auditoria.objects.create(
        accion=accion,
        tabla=sender._meta.model_name,
        registro_id=instance.pk,
        valor_nuevo=get_model_data(instance),
        valor_anterior=None,
    )


def auditoria_post_delete(sender, instance, **kwargs):
    Auditoria.objects.create(
        accion='DELETE',
        tabla=sender._meta.model_name,
        registro_id=instance.pk,
        valor_anterior=get_model_data(instance),
    )


# Registrar signals SOLO para los modelos que queremos auditar
for _model in MODELS_TO_TRACK:
    post_save.connect(auditoria_post_save, sender=_model)
    post_delete.connect(auditoria_post_delete, sender=_model)
