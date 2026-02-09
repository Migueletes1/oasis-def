import os
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator

from OASIS.utils import format_bytes


CLUSTER_CHOICES = [
    ('TICS', 'Tecnologias de la Informacion'),
    ('ADMIN', 'Ciencias Administrativas'),
    ('SALUD', 'Salud y Bienestar'),
    ('INDUSTRIAL', 'Ingenieria e Industria'),
    ('CREATIVAS', 'Artes y Diseno'),
    ('AGRO', 'Agroindustria y Ambiente'),
    ('TURISMO', 'Turismo y Gastronomia'),
]

CARRERA_CHOICES = [
    # ── TICs ──
    ('software', 'Desarrollo de Software'),
    ('animacion_3d', 'Animacion 3D y Efectos Visuales'),
    ('adsi', 'Analisis y Desarrollo de Sistemas'),
    ('multimedia', 'Produccion de Multimedia'),
    ('redes', 'Administracion de Redes'),
    ('telecomunicaciones', 'Telecomunicaciones'),
    ('videojuegos', 'Diseno de Videojuegos'),
    ('ia', 'Inteligencia Artificial'),
    ('ciberseguridad', 'Ciberseguridad'),
    ('ciencia_datos', 'Ciencia de Datos'),
    # ── Administrativas ──
    ('contabilidad', 'Contabilidad y Finanzas'),
    ('gestion_admin', 'Gestion Administrativa'),
    ('talento_humano', 'Gestion del Talento Humano'),
    ('gestion_empresarial', 'Gestion Empresarial'),
    ('negocios_int', 'Negociacion Internacional'),
    ('logistica', 'Gestion Logistica'),
    ('bancaria', 'Gestion Bancaria y Financiera'),
    ('mercados', 'Gestion de Mercados'),
    ('comercio_int', 'Comercio Internacional'),
    # ── Salud ──
    ('enfermeria', 'Enfermeria'),
    ('salud_ocup', 'Salud Ocupacional'),
    ('farmacia', 'Regencia de Farmacia'),
    ('primera_infancia', 'Atencion a la Primera Infancia'),
    ('sst', 'Seguridad y Salud en el Trabajo'),
    ('nutricion', 'Nutricion y Dietetica'),
    ('imagenes_dx', 'Imagenes Diagnosticas'),
    # ── Industriales ──
    ('electricidad', 'Electricidad Industrial'),
    ('electronica', 'Electronica'),
    ('mecanica', 'Mecanica Industrial'),
    ('automatizacion', 'Automatizacion Industrial'),
    ('electromecanica', 'Mantenimiento Electromecanico'),
    ('construccion', 'Construccion'),
    ('mecatronica', 'Mecatronica'),
    ('diseno_industrial', 'Diseno Industrial'),
    # ── Creativas ──
    ('diseno_grafico', 'Diseno Grafico'),
    ('audiovisual', 'Produccion Audiovisual'),
    ('comunicacion', 'Comunicacion Comercial'),
    ('fotografia', 'Fotografia'),
    ('modas', 'Diseno de Modas'),
    # ── Agro y Ambiente ──
    ('ambiental', 'Gestion Ambiental'),
    ('agroindustria', 'Agroindustria Alimentaria'),
    ('agropecuaria', 'Produccion Agropecuaria'),
    # ── Turismo ──
    ('gastronomia', 'Gastronomia'),
    ('hotelera', 'Gestion Hotelera'),
]

CARRERA_A_CLUSTER = {
    'software': 'TICS', 'animacion_3d': 'TICS', 'adsi': 'TICS',
    'multimedia': 'TICS', 'redes': 'TICS', 'telecomunicaciones': 'TICS',
    'videojuegos': 'TICS', 'ia': 'TICS', 'ciberseguridad': 'TICS',
    'ciencia_datos': 'TICS',
    'contabilidad': 'ADMIN', 'gestion_admin': 'ADMIN', 'talento_humano': 'ADMIN',
    'gestion_empresarial': 'ADMIN', 'negocios_int': 'ADMIN', 'logistica': 'ADMIN',
    'bancaria': 'ADMIN', 'mercados': 'ADMIN', 'comercio_int': 'ADMIN',
    'enfermeria': 'SALUD', 'salud_ocup': 'SALUD', 'farmacia': 'SALUD',
    'primera_infancia': 'SALUD', 'sst': 'SALUD', 'nutricion': 'SALUD',
    'imagenes_dx': 'SALUD',
    'electricidad': 'INDUSTRIAL', 'electronica': 'INDUSTRIAL', 'mecanica': 'INDUSTRIAL',
    'automatizacion': 'INDUSTRIAL', 'electromecanica': 'INDUSTRIAL',
    'construccion': 'INDUSTRIAL', 'mecatronica': 'INDUSTRIAL',
    'diseno_industrial': 'INDUSTRIAL',
    'diseno_grafico': 'CREATIVAS', 'audiovisual': 'CREATIVAS',
    'comunicacion': 'CREATIVAS', 'fotografia': 'CREATIVAS', 'modas': 'CREATIVAS',
    'ambiental': 'AGRO', 'agroindustria': 'AGRO', 'agropecuaria': 'AGRO',
    'gastronomia': 'TURISMO', 'hotelera': 'TURISMO',
}

# ── Preview type mapping by career ──
PREVIEW_TYPE_CHOICES = [
    ('CODE', 'Visor de Codigo'),
    ('MEDIA_3D', 'Modelo 3D / Animacion'),
    ('GALLERY', 'Galeria de Imagenes'),
    ('DOCUMENT', 'Documento / PDF'),
    ('VIDEO', 'Video / Multimedia'),
]

CARRERA_A_PREVIEW = {
    # CODE-based careers
    'software': 'CODE', 'adsi': 'CODE', 'redes': 'CODE',
    'telecomunicaciones': 'CODE', 'ia': 'CODE', 'ciberseguridad': 'CODE',
    'ciencia_datos': 'CODE',
    # 3D/Animation
    'animacion_3d': 'MEDIA_3D', 'videojuegos': 'MEDIA_3D', 'mecatronica': 'MEDIA_3D',
    # Gallery/Visual
    'diseno_grafico': 'GALLERY', 'fotografia': 'GALLERY', 'modas': 'GALLERY',
    'diseno_industrial': 'GALLERY', 'multimedia': 'GALLERY',
    # Video/Multimedia
    'audiovisual': 'VIDEO', 'comunicacion': 'VIDEO',
    # Document-based (everything else defaults to DOCUMENT)
}

# ── Unified extension → (tipo, icon_class) mapping ──
# Single source of truth for both detect_tipo() and icon_class property
EXTENSION_MAP = {
    # Documents
    'pdf': ('documento', 'fa-file-pdf text-red-500'),
    'doc': ('documento', 'fa-file-word text-blue-500'),
    'docx': ('documento', 'fa-file-word text-blue-500'),
    'txt': ('documento', 'fa-file-lines text-gray-500'),
    'md': ('documento', 'fa-file-lines text-gray-500'),
    'csv': ('documento', 'fa-file-csv text-green-600'),
    # Code
    'py': ('codigo', 'fa-file-code text-yellow-500'),
    'js': ('codigo', 'fa-file-code text-yellow-500'),
    'html': ('codigo', 'fa-file-code text-orange-400'),
    'css': ('codigo', 'fa-file-code text-blue-400'),
    'java': ('codigo', 'fa-file-code text-red-400'),
    'cpp': ('codigo', 'fa-file-code text-purple-500'),
    'c': ('codigo', 'fa-file-code text-purple-400'),
    'cs': ('codigo', 'fa-file-code text-violet-500'),
    'ts': ('codigo', 'fa-file-code text-blue-500'),
    'jsx': ('codigo', 'fa-file-code text-cyan-500'),
    'tsx': ('codigo', 'fa-file-code text-cyan-500'),
    'json': ('codigo', 'fa-file-code text-gray-500'),
    'xml': ('codigo', 'fa-file-code text-gray-500'),
    'sql': ('codigo', 'fa-file-code text-amber-500'),
    # Images
    'jpg': ('imagen', 'fa-file-image text-pink-500'),
    'jpeg': ('imagen', 'fa-file-image text-pink-500'),
    'png': ('imagen', 'fa-file-image text-pink-500'),
    'gif': ('imagen', 'fa-file-image text-purple-400'),
    'svg': ('imagen', 'fa-file-image text-green-500'),
    'webp': ('imagen', 'fa-file-image text-pink-400'),
    'bmp': ('imagen', 'fa-file-image text-pink-400'),
    'psd': ('imagen', 'fa-file-image text-blue-600'),
    'ai': ('imagen', 'fa-file-image text-orange-500'),
    # Video
    'mp4': ('video', 'fa-file-video text-blue-600'),
    'avi': ('video', 'fa-file-video text-blue-600'),
    'mov': ('video', 'fa-file-video text-blue-600'),
    'mkv': ('video', 'fa-file-video text-blue-600'),
    'webm': ('video', 'fa-file-video text-blue-600'),
    # Audio
    'mp3': ('otro', 'fa-file-audio text-violet-500'),
    'wav': ('otro', 'fa-file-audio text-violet-500'),
    'ogg': ('otro', 'fa-file-audio text-violet-500'),
    # 3D Models
    'obj': ('modelo_3d', 'fa-cube text-teal-500'),
    'fbx': ('modelo_3d', 'fa-cube text-teal-500'),
    'stl': ('modelo_3d', 'fa-cube text-teal-500'),
    'gltf': ('modelo_3d', 'fa-cube text-teal-500'),
    'glb': ('modelo_3d', 'fa-cube text-teal-500'),
    'blend': ('modelo_3d', 'fa-cube text-orange-500'),
    # Presentations
    'ppt': ('presentacion', 'fa-file-powerpoint text-orange-500'),
    'pptx': ('presentacion', 'fa-file-powerpoint text-orange-500'),
    # Spreadsheets
    'xls': ('documento', 'fa-file-excel text-green-600'),
    'xlsx': ('documento', 'fa-file-excel text-green-600'),
    # Archives
    'zip': ('comprimido', 'fa-file-zipper text-amber-600'),
    'rar': ('comprimido', 'fa-file-zipper text-amber-600'),
    '7z': ('comprimido', 'fa-file-zipper text-amber-600'),
    'tar': ('comprimido', 'fa-file-zipper text-amber-600'),
    'gz': ('comprimido', 'fa-file-zipper text-amber-600'),
    # Design
    'fig': ('imagen', 'fa-file-image text-purple-500'),
    'sketch': ('imagen', 'fa-file-image text-orange-400'),
}

ALLOWED_EXTENSIONS = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'cs', 'ts', 'jsx', 'tsx',
    'json', 'xml', 'sql', 'txt', 'md', 'csv',
    'zip', 'rar', '7z', 'tar', 'gz',
    'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'bmp',
    'mp4', 'avi', 'mov', 'mkv', 'webm',
    'mp3', 'wav', 'ogg',
    'obj', 'fbx', 'stl', 'gltf', 'glb', 'blend',
    'psd', 'ai', 'fig', 'sketch',
]


def proyecto_upload_path(instance, filename):
    """Generates: media/repositorio/<carrera>/<year>/<uuid>_<filename>"""
    safe_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    pub_date = getattr(instance.proyecto, 'fecha_publicacion', None)
    year = pub_date.year if pub_date else instance.proyecto.anio
    return os.path.join('repositorio', instance.proyecto.carrera, str(year), safe_name)


def thumbnail_upload_path(instance, filename):
    """Generates: media/repositorio/thumbnails/<uuid>_<filename>"""
    safe_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    return os.path.join('repositorio', 'thumbnails', safe_name)


class TagHabilidad(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    categoria = models.CharField(max_length=50, blank=True,
                                 help_text='Ej: Lenguaje, Framework, Herramienta, Metodologia')

    class Meta:
        verbose_name = 'Tag / Habilidad'
        verbose_name_plural = 'Tags / Habilidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ProyectoGrado(models.Model):

    class EstadoProyecto(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        EN_REVISION = 'en_revision', 'En Revision'
        PUBLICADO = 'publicado', 'Publicado'
        RECHAZADO = 'rechazado', 'Rechazado'

    class VersionLabel(models.TextChoices):
        V1 = 'V1', 'Version 1 (Borrador)'
        V2 = 'V2', 'Version 2 (Revision)'
        FINAL = 'FINAL', 'Version Final'

    # ── Core fields ──
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    resumen = models.TextField(blank=True, help_text='Resumen ejecutivo (max 500 chars)')
    carrera = models.CharField(max_length=50, choices=CARRERA_CHOICES)

    # ── Authors and relationships ──
    autor = models.CharField(max_length=200)
    email_autor = models.EmailField(blank=True)
    ficha = models.CharField(max_length=20, blank=True,
                             help_text='Numero de ficha SENA')
    instructor_avalador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='proyectos_avalados',
        limit_choices_to={'rol': 'instructor'},
    )
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='proyectos_subidos',
    )

    # ── Media and links ──
    thumbnail = models.ImageField(
        upload_to=thumbnail_upload_path, blank=True, null=True,
        help_text='Miniatura del proyecto (recomendado: 400x300px)',
    )
    imagen_url = models.URLField(
        blank=True,
        help_text='URL de imagen externa (alternativa a thumbnail)',
    )
    enlace_repositorio = models.URLField(blank=True,
                                         help_text='Link GitHub/GitLab/externo')
    enlace_demo = models.URLField(blank=True, help_text='Link demo en vivo')

    # ── Metadata ──
    anio = models.PositiveIntegerField(
        default=2026, validators=[MinValueValidator(2020), MaxValueValidator(2035)],
        help_text='Ano de presentacion',
    )
    tags = models.ManyToManyField(TagHabilidad, blank=True, related_name='proyectos')
    herramientas_usadas = models.CharField(max_length=500, blank=True,
                                           help_text='Ej: Python, React, Figma (separado por comas)')
    version_actual = models.CharField(max_length=5, choices=VersionLabel.choices,
                                      default=VersionLabel.V1)
    estado = models.CharField(max_length=15, choices=EstadoProyecto.choices,
                              default=EstadoProyecto.BORRADOR)

    # ── Stats ──
    votos = models.PositiveIntegerField(default=0)
    descargas = models.PositiveIntegerField(default=0)
    vistas = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-destacado', '-votos', '-fecha_publicacion']
        verbose_name = 'Proyecto de Grado'
        verbose_name_plural = 'Proyectos de Grado'

    def __str__(self):
        return f"{self.titulo} — {self.get_carrera_display()}"

    @property
    def cluster(self):
        return CARRERA_A_CLUSTER.get(self.carrera, 'TICS')

    @property
    def cluster_display(self):
        cluster_key = self.cluster
        return dict(CLUSTER_CHOICES).get(cluster_key, cluster_key)

    @property
    def preview_type(self):
        return CARRERA_A_PREVIEW.get(self.carrera, 'DOCUMENT')

    @property
    def preview_type_display(self):
        return dict(PREVIEW_TYPE_CHOICES).get(self.preview_type, 'Documento')

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        if self.imagen_url:
            return self.imagen_url
        return None

    @property
    def tags_list(self):
        if self.herramientas_usadas:
            return [t.strip() for t in self.herramientas_usadas.split(',') if t.strip()]
        return []

    @property
    def archivos_count(self):
        # Use len() to leverage prefetch_related cache instead of hitting DB
        return len(self.archivos.all())

    @property
    def es_publicado(self):
        return self.estado == self.EstadoProyecto.PUBLICADO


class ArchivoProyecto(models.Model):
    """Individual file attached to a project (supports multi-file uploads)."""

    class TipoArchivo(models.TextChoices):
        DOCUMENTO = 'documento', 'Documento'
        CODIGO = 'codigo', 'Codigo Fuente'
        IMAGEN = 'imagen', 'Imagen'
        VIDEO = 'video', 'Video'
        MODELO_3D = 'modelo_3d', 'Modelo 3D'
        PRESENTACION = 'presentacion', 'Presentacion'
        COMPRIMIDO = 'comprimido', 'Archivo Comprimido'
        OTRO = 'otro', 'Otro'

    proyecto = models.ForeignKey(
        ProyectoGrado, on_delete=models.CASCADE, related_name='archivos',
    )
    archivo = models.FileField(
        upload_to=proyecto_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
    )
    nombre_original = models.CharField(max_length=255)
    tipo = models.CharField(max_length=15, choices=TipoArchivo.choices,
                            default=TipoArchivo.OTRO)
    size_bytes = models.BigIntegerField(default=0)
    hash_sha256 = models.CharField(max_length=64, blank=True,
                                   help_text='Hash de integridad')
    scan_status = models.CharField(max_length=20, default='pending',
                                   choices=[('pending', 'Pendiente'),
                                            ('clean', 'Limpio'),
                                            ('suspicious', 'Sospechoso')])
    version_label = models.CharField(
        max_length=5, choices=ProyectoGrado.VersionLabel.choices,
        default=ProyectoGrado.VersionLabel.V1,
    )
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_subida']
        verbose_name = 'Archivo de Proyecto'
        verbose_name_plural = 'Archivos de Proyecto'

    def __str__(self):
        return f"{self.nombre_original} ({self.proyecto.titulo})"

    @property
    def extension(self):
        return self.nombre_original.rsplit('.', 1)[-1].lower() if '.' in self.nombre_original else ''

    @property
    def size_display(self):
        return format_bytes(self.size_bytes)

    @property
    def icon_class(self):
        entry = EXTENSION_MAP.get(self.extension)
        return entry[1] if entry else 'fa-file text-gray-400'

    def detect_tipo(self):
        """Auto-detect file type from extension using EXTENSION_MAP."""
        entry = EXTENSION_MAP.get(self.extension)
        return entry[0] if entry else 'otro'


class RegistroDescarga(models.Model):
    """Tracks who downloaded what and when (audit trail)."""
    archivo = models.ForeignKey(ArchivoProyecto, on_delete=models.CASCADE,
                                related_name='descargas_log')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Registro de Descarga'
        verbose_name_plural = 'Registros de Descarga'

    def __str__(self):
        user = self.usuario.username if self.usuario else 'Anonimo'
        return f"{user} -> {self.archivo.nombre_original}"


class Carrera(models.Model):
    """Carrera model for admin CRUD. Source of truth for career management."""
    clave = models.CharField(max_length=50, unique=True,
                             help_text='Clave interna (ej: software)')
    nombre = models.CharField(max_length=200,
                              help_text='Nombre completo de la carrera')
    cluster = models.CharField(max_length=20, choices=CLUSTER_CHOICES)
    icono = models.CharField(max_length=100, blank=True, default='fa-graduation-cap',
                             help_text='Clase FontAwesome (ej: fa-code)')
    descripcion = models.TextField(blank=True,
                                   help_text='Descripcion breve de la carrera')
    activa = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['cluster', 'orden', 'nombre']
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'

    def __str__(self):
        return f"{self.nombre} ({self.get_cluster_display()})"

    @property
    def cluster_display(self):
        return dict(CLUSTER_CHOICES).get(self.cluster, self.cluster)
