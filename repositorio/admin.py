from django.contrib import admin
from .models import ProyectoGrado, ArchivoProyecto, TagHabilidad, RegistroDescarga, Carrera


class ArchivoInline(admin.TabularInline):
    model = ArchivoProyecto
    extra = 0
    readonly_fields = ['size_bytes', 'hash_sha256', 'scan_status', 'fecha_subida']
    fields = ['archivo', 'nombre_original', 'tipo', 'version_label', 'size_bytes',
              'scan_status', 'fecha_subida']


@admin.register(ProyectoGrado)
class ProyectoGradoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'carrera', 'autor', 'ficha', 'estado', 'version_actual',
                    'votos', 'descargas', 'destacado', 'fecha_publicacion']
    list_filter = ['carrera', 'estado', 'destacado', 'version_actual', 'anio']
    search_fields = ['titulo', 'autor', 'descripcion', 'ficha']
    list_editable = ['destacado', 'estado']
    readonly_fields = ['vistas', 'descargas', 'fecha_publicacion', 'fecha_actualizacion']
    filter_horizontal = ['tags']
    inlines = [ArchivoInline]
    fieldsets = (
        ('Informacion Principal', {
            'fields': ('titulo', 'descripcion', 'resumen', 'carrera', 'anio')
        }),
        ('Autores', {
            'fields': ('autor', 'email_autor', 'ficha', 'instructor_avalador', 'subido_por')
        }),
        ('Media y Enlaces', {
            'fields': ('thumbnail', 'imagen_url', 'enlace_repositorio', 'enlace_demo')
        }),
        ('Metadata', {
            'fields': ('tags', 'herramientas_usadas', 'version_actual', 'estado')
        }),
        ('Estadisticas', {
            'fields': ('votos', 'descargas', 'vistas', 'destacado',
                       'fecha_publicacion', 'fecha_actualizacion')
        }),
    )


@admin.register(TagHabilidad)
class TagHabilidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'categoria']
    list_filter = ['categoria']
    search_fields = ['nombre']
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(ArchivoProyecto)
class ArchivoProyectoAdmin(admin.ModelAdmin):
    list_display = ['nombre_original', 'proyecto', 'tipo', 'version_label',
                    'size_display', 'scan_status', 'fecha_subida']
    list_filter = ['tipo', 'scan_status', 'version_label']
    search_fields = ['nombre_original', 'proyecto__titulo']
    readonly_fields = ['hash_sha256', 'size_bytes']


@admin.register(RegistroDescarga)
class RegistroDescargaAdmin(admin.ModelAdmin):
    list_display = ['archivo', 'usuario', 'ip_address', 'fecha']
    list_filter = ['fecha']
    readonly_fields = ['archivo', 'usuario', 'ip_address', 'fecha']


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ['clave', 'nombre', 'cluster', 'icono', 'activa', 'orden']
    list_filter = ['cluster', 'activa']
    search_fields = ['nombre', 'clave']
    list_editable = ['activa', 'orden']
