from django.db import migrations


def create_sql_view(apps, schema_editor):
    if schema_editor.connection.vendor == 'mysql':
        schema_editor.execute("""
            CREATE OR REPLACE VIEW vw_asignaciones_detalle AS
            SELECT
                a.id,
                p.nombre as proyecto_nombre,
                p.codigo as proyecto_codigo,
                CONCAT(ap.nombres, ' ', ap.apellidos) as aprendiz_nombre,
                CONCAT(i.nombres, ' ', i.apellidos) as instructor_nombre,
                a.fecha_inicio,
                a.fecha_fin,
                a.activo
            FROM asignaciones_asignacion a
            JOIN proyectos_proyecto p ON a.proyecto_id = p.id
            JOIN aprendices_aprendiz ap ON a.aprendiz_id = ap.id
            LEFT JOIN instructores_instructor i ON a.instructor_id = i.id;
        """)
    elif schema_editor.connection.vendor == 'sqlite':
        schema_editor.execute("""
            CREATE VIEW IF NOT EXISTS vw_asignaciones_detalle AS
            SELECT
                a.id,
                p.nombre as proyecto_nombre,
                p.codigo as proyecto_codigo,
                (ap.nombres || ' ' || ap.apellidos) as aprendiz_nombre,
                (i.nombres || ' ' || i.apellidos) as instructor_nombre,
                a.fecha_inicio,
                a.fecha_fin,
                a.activo
            FROM asignaciones_asignacion a
            JOIN proyectos_proyecto p ON a.proyecto_id = p.id
            JOIN aprendices_aprendiz ap ON a.aprendiz_id = ap.id
            LEFT JOIN instructores_instructor i ON a.instructor_id = i.id;
        """)


def drop_sql_view(apps, schema_editor):
    schema_editor.execute("DROP VIEW IF EXISTS vw_asignaciones_detalle;")


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0001_initial'),
        ('asignaciones', '0001_initial'),
        ('proyectos', '0001_initial'),
        ('aprendices', '0001_initial'),
        ('instructores', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_sql_view, drop_sql_view),
    ]
