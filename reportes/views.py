from rest_framework import serializers, viewsets
from rest_framework.response import Response
from django.db import connection

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Serializer for the SQL View result (not a model serializer)
class ReporteAsignacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    proyecto_nombre = serializers.CharField()
    proyecto_codigo = serializers.CharField()
    aprendiz_nombre = serializers.CharField()
    instructor_nombre = serializers.CharField(allow_null=True)
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    activo = serializers.BooleanField()

class ReporteViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing reports.
    """
    @method_decorator(cache_page(60*15)) # Cache for 15 minutes
    def list(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM vw_asignaciones_detalle")
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        serializer = ReporteAsignacionSerializer(results, many=True)
        return Response(serializer.data)
