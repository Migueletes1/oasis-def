# 📊 Módulo de Carga Masiva por CSV - OASIS

## 🎯 Descripción General

El Módulo de Carga Masiva permite al Administrador registrar cientos de **Aprendices** e **Instructores** simultáneamente mediante archivos CSV, con validaciones robustas y procesamiento transaccional.

---

## 🚀 Características Implementadas

### ✅ Frontend (HTML/Tailwind/JavaScript)

#### 1. **Zona de Dropzone Interactiva**
- Arrastrar y soltar archivos CSV
- Bordes punteados en verde OASIS
- Validación de extensión (.csv)
- Validación de tamaño (máximo 5MB)
- Preview del archivo seleccionado

#### 2. **Descarga de Plantilla CSV**
- Botón naranja destacado
- Genera archivos de ejemplo con columnas correctas
- Dos tipos: `plantilla_aprendices.csv` y `plantilla_instructores.csv`
- Incluye filas de ejemplo

#### 3. **Visualizador de Errores Pre-carga**
- Tabla detallada con:
  - **Fila**: Número de línea con error
  - **Campo**: Columna problemática
  - **Error**: Descripción específica
- Fondo naranja/rojo para errores
- Listado de carreras sugeridas cuando hay error de carrera

#### 4. **Barra de Progreso Real**
- Animación verde OASIS
- Porcentaje en tiempo real
- Texto descriptivo del proceso
- Transiciones suaves

#### 5. **Panel de Éxito**
- Fondo verde con icono de check
- Contador de usuarios creados
- Tabla con credenciales temporales
- Botón para descargar CSV de credenciales

---

### ✅ Backend (Django)

#### 1. **Vista Principal: `carga_masiva_view()`**
```python
@admin_required
def carga_masiva_view(request):
    """Vista principal del módulo de carga masiva."""
    return render(request, 'usuarios/carga_masiva.html')
```

#### 2. **Descarga de Plantilla: `descargar_plantilla_csv()`**
- Genera CSV con columnas correctas
- Incluye BOM UTF-8 para Excel
- Filas de ejemplo realistas
- Parámetro `?tipo=aprendices` o `?tipo=instructores`

**Columnas para Aprendices:**
```csv
tipo_documento,numero_documento,nombres,apellidos,email,telefono,carrera
CC,1234567890,Juan,Pérez,juan.perez@example.com,3001234567,Desarrollo de Software
```

**Columnas para Instructores:**
```csv
tipo_documento,numero_documento,nombres,apellidos,email,especialidad
CC,1234567890,Carlos,Rodríguez,carlos.rodriguez@example.com,Desarrollo de Software
```

#### 3. **Procesamiento de CSV: `procesar_csv()`**

**Flujo de Procesamiento:**

```
1. Validación de Archivo
   ├─ MIME type (text/csv)
   ├─ Tamaño (max 5MB)
   └─ Decodificación (UTF-8 o Latin-1)

2. Parseo con csv.DictReader
   └─ Lectura línea por línea

3. Validación de Filas (max 2,000)
   ├─ Campos requeridos
   ├─ Formato de email
   ├─ Duplicados en BD
   └─ Carrera válida (solo aprendices)

4. Creación Transaccional
   ├─ transaction.atomic()
   ├─ Usuario + Aprendiz/Instructor
   ├─ Contraseña temporal
   └─ Rollback si falla
```

---

## 🔐 Seguridad y Ciberseguridad

### 1. **Validación de MIME Type**
```python
if archivo.content_type not in ['text/csv', 'application/vnd.ms-excel']:
    return JsonResponse({'error': 'Tipo de archivo no permitido'}, status=400)
```

### 2. **Sanitización de Datos**
```python
def _sanitizar_texto(texto):
    """Limpia espacios en blanco y caracteres especiales."""
    if not texto:
        return ''
    return texto.strip().replace('\n', '').replace('\r', '')
```

Aplica a:
- Nombres
- Apellidos
- Emails
- Números de documento
- Especialidades
- Nombres de carreras

### 3. **Límite de Carga**
```python
MAX_FILAS = 2000

if filas_procesadas > MAX_FILAS:
    errores.append({
        'fila': i,
        'campo': 'general',
        'error': f'Se excedió el límite máximo de {MAX_FILAS} filas'
    })
    break
```

### 4. **Validación de Email**
```python
from django.core.validators import validate_email

def _validar_email(email):
    try:
        validate_email(email)
        return True, None
    except ValidationError:
        return False, "Formato de email inválido"
```

### 5. **Prevención de Duplicados**
```python
# Validar email único
if Usuario.objects.filter(username=email).exists():
    errores.append({'fila': i, 'campo': 'email', 'error': 'Email ya registrado'})

# Validar documento único
if Aprendiz.objects.filter(numero_documento=numero_doc).exists():
    errores.append({'fila': i, 'campo': 'numero_documento', 'error': 'Documento ya registrado'})
```

### 6. **Generación de Contraseñas Seguras**
```python
def _generar_contrasena_temporal():
    """Genera contraseña aleatoria de 12 caracteres con:
    - Al menos 1 mayúscula
    - Al menos 1 número
    - Al menos 1 carácter especial
    """
    chars = string.ascii_letters + string.digits + string.punctuation
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation),
    ]
    password += [secrets.choice(chars) for _ in range(9)]
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)
```

Ejemplo de contraseña generada: `8M$kd2P!vQzA`

### 7. **Transacciones Atómicas**
```python
with transaction.atomic():
    for data in usuarios_creados:
        # Crear Usuario
        usuario = Usuario.objects.create_user(...)

        # Crear Aprendiz/Instructor
        aprendiz = Aprendiz.objects.create(...)
```

Si falla cualquier creación, **todo se revierte** (rollback automático).

---

## 📋 Validación de las 44 Carreras

### Función de Validación

```python
def _validar_carrera(nombre_carrera):
    """Valida que la carrera exista en las 44 permitidas."""
    from repositorio.models import Carrera

    nombre_sanitizado = _sanitizar_texto(nombre_carrera).lower()

    # Buscar por nombre
    carrera = Carrera.objects.filter(activa=True).filter(
        nombre__iexact=nombre_sanitizado
    ).first()

    if not carrera:
        # Intentar por clave
        carrera = Carrera.objects.filter(activa=True).filter(
            clave__iexact=nombre_sanitizado
        ).first()

    if carrera:
        return True, None, carrera

    # Error con lista de carreras disponibles
    carreras_disponibles = Carrera.objects.filter(activa=True).values_list('nombre', flat=True)
    return False, f"La carrera '{nombre_carrera}' no existe. Carreras disponibles: ...", None
```

### ¿Cómo se manejan las 44 carreras?

#### 1. **Búsqueda Case-Insensitive**
El usuario puede escribir:
- `"Desarrollo de Software"` ✅
- `"desarrollo de software"` ✅
- `"DESARROLLO DE SOFTWARE"` ✅
- `"software"` ✅ (por clave)

#### 2. **Búsqueda por Nombre o Clave**
```python
# Por nombre completo
'Desarrollo de Software' → ✅

# Por clave
'software' → ✅
'animacion_3d' → ✅
'mecanica_automotriz' → ✅
```

#### 3. **Solo Carreras Activas**
```python
Carrera.objects.filter(activa=True)
```
Filtra solo carreras con `activa=True` en la base de datos.

#### 4. **Mensaje de Error Detallado**
Si el usuario escribe `"Ingeniería"`:

```json
{
  "fila": 5,
  "campo": "carrera",
  "error": "La carrera 'Ingeniería' no existe. Carreras disponibles: Desarrollo de Software, Animación 3D y Efectos Visuales, Ciberseguridad, Administración de Redes, Gestión Empresarial..."
}
```

---

## 📊 Estructura de Datos de Respuesta

### Respuesta de Éxito

```json
{
  "success": true,
  "usuarios_creados": 15,
  "detalle": [
    {
      "email": "juan.perez@example.com",
      "nombre": "Juan Pérez",
      "password_temporal": "8M$kd2P!vQzA"
    },
    {
      "email": "maria.gonzalez@example.com",
      "nombre": "María González",
      "password_temporal": "3X@tz9N!bKmL"
    }
  ]
}
```

### Respuesta de Error

```json
{
  "success": false,
  "errores": [
    {
      "fila": 3,
      "campo": "email",
      "error": "Formato de email inválido"
    },
    {
      "fila": 5,
      "campo": "carrera",
      "error": "La carrera 'Ingeniería' no existe. Carreras disponibles: ..."
    },
    {
      "fila": 7,
      "campo": "numero_documento",
      "error": "El documento 1234567890 ya está registrado"
    }
  ],
  "filas_procesadas": 10
}
```

---

## 🎨 Paleta de Colores Implementada

### 60% - Blanco (Fondo)
```css
background-color: #ffffff;  /* Paneles */
background-color: #f9fafb;  /* Fondo general */
```

### 30% - Naranja (Botones, Alertas)
```css
/* Botón de descarga de plantilla */
background: linear-gradient(to right, #f97316, #ea580c);

/* Panel de errores */
background: linear-gradient(to right, #ef4444, #f97316);

/* Acentos */
color: #f97316;
```

### 10% - Verde (Progreso, Éxito)
```css
/* Barra de progreso */
background: linear-gradient(to right, #10b981, #059669);

/* Panel de éxito */
background: linear-gradient(to right, #10b981, #059669);

/* Bordes dropzone */
border-color: #10b981;
```

---

## 🔧 Funcionalidades Adicionales

### 1. **Descarga de Credenciales**
Al finalizar la carga, el admin puede descargar un CSV con:
```csv
Nombre,Email,Contraseña Temporal
"Juan Pérez","juan.perez@example.com","8M$kd2P!vQzA"
"María González","maria.gonzalez@example.com","3X@tz9N!bKmL"
```

### 2. **Logging Completo**
```python
logger.info(f"Plantilla CSV descargada: {tipo} por {request.user.username}")
logger.info(f"Carga masiva exitosa: {len(usuarios_creados_exitosos)} {tipo} creados por {request.user.username}")
logger.error(f"Error en carga masiva: {str(e)}")
```

### 3. **Protección CSRF**
```html
{% csrf_token %}
```
```javascript
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
fetch('...', {
    headers: { 'X-CSRFToken': csrftoken }
})
```

### 4. **Decorador de Admin**
```python
@admin_required
def carga_masiva_view(request):
    ...
```
Solo usuarios con `rol='admin'` o `is_superuser=True` pueden acceder.

---

## 📝 Uso del Módulo

### Paso 1: Acceder al Módulo
```
URL: /usuarios/admin/carga-masiva/
```

### Paso 2: Seleccionar Tipo
- Hacer clic en el botón de **Aprendices** o **Instructores**

### Paso 3: Descargar Plantilla
- Hacer clic en "Descargar Plantilla CSV"
- Se descarga `plantilla_aprendices.csv` o `plantilla_instructores.csv`

### Paso 4: Llenar el CSV
Abrir en Excel/LibreOffice/Google Sheets y llenar las columnas:

**Para Aprendices:**
```
tipo_documento | numero_documento | nombres | apellidos | email | telefono | carrera
CC             | 1234567890       | Juan    | Pérez     | juan@...| 3001... | Desarrollo de Software
TI             | 9876543210       | María   | González  | maria@..| 3109... | Animación 3D y Efectos Visuales
```

**Para Instructores:**
```
tipo_documento | numero_documento | nombres | apellidos | email | especialidad
CC             | 1234567890       | Carlos  | Rodríguez | carlos@...| Bases de Datos
```

### Paso 5: Subir el Archivo
- Arrastrar el CSV a la zona de dropzone
- O hacer clic para seleccionar

### Paso 6: Procesar
- Hacer clic en "Procesar Archivo CSV"
- Esperar a que finalice la barra de progreso

### Paso 7: Revisar Resultados
- **Si hay errores:** Corregir el CSV y volver a intentar
- **Si es exitoso:** Descargar las credenciales generadas

---

## 🐛 Manejo de Errores Comunes

### Error: "Tipo de archivo no permitido"
**Causa:** El archivo no es CSV
**Solución:** Guardar el archivo con extensión `.csv` en formato CSV

### Error: "El archivo es demasiado grande"
**Causa:** El archivo pesa más de 5MB
**Solución:** Dividir en múltiples archivos más pequeños

### Error: "Se excedió el límite máximo de 2000 filas"
**Causa:** El CSV tiene más de 2000 filas
**Solución:** Dividir en archivos de máximo 2000 filas cada uno

### Error: "Formato de email inválido"
**Causa:** El email no cumple el formato estándar
**Solución:** Verificar que sea del tipo `usuario@dominio.com`

### Error: "La carrera 'X' no existe"
**Causa:** La carrera no está en las 44 permitidas
**Solución:** Usar uno de los nombres exactos listados en el error

### Error: "El email X ya está registrado"
**Causa:** El email ya existe en la base de datos
**Solución:** Usar un email diferente

### Error: "El documento X ya está registrado"
**Causa:** El número de documento ya existe
**Solución:** Verificar que no esté duplicado en el CSV o en la BD

---

## 📦 Dependencias

```python
# Ya incluidas en el proyecto
import csv           # Parseo de CSV
import io            # Manejo de streams
import secrets       # Generación de contraseñas seguras
import string        # Caracteres para contraseñas
from django.db import transaction  # Transacciones atómicas
from django.core.validators import validate_email  # Validación de email
```

---

## 🚀 Mejoras Futuras (Opcionales)

### 1. **Envío de Correos Electrónicos**
```python
from django.core.mail import send_mail

send_mail(
    subject='Bienvenido a OASIS',
    message=f'Tu contraseña temporal es: {password_temporal}',
    from_email='noreply@oasis.edu.co',
    recipient_list=[email],
)
```

### 2. **Procesamiento Asíncrono con Celery**
Para archivos muy grandes:
```python
from celery import shared_task

@shared_task
def procesar_csv_async(archivo_path):
    # Procesar en background
    ...
```

### 3. **Validación de Campos Adicionales**
- Validar formato de teléfono (10 dígitos)
- Validar formato de documento según tipo (CC: 6-10 dígitos)

### 4. **Integración con Active Directory**
Sincronizar usuarios creados con AD del SENA

### 5. **Preview de Filas antes de Procesar**
Mostrar las primeras 10 filas parseadas antes de confirmar la carga

---

## 📞 Soporte

Para problemas o preguntas, contactar al equipo de desarrollo de OASIS.

---

## ✅ Checklist de Implementación

- [x] Vista de carga masiva (`carga_masiva_view`)
- [x] Vista de descarga de plantilla (`descargar_plantilla_csv`)
- [x] Vista de procesamiento (`procesar_csv`)
- [x] Template HTML con dropzone
- [x] JavaScript para barra de progreso
- [x] Validación de MIME type
- [x] Sanitización de datos
- [x] Límite de 2000 filas
- [x] Validación de las 44 carreras
- [x] Generación de contraseñas temporales
- [x] Transacciones atómicas
- [x] Manejo de errores detallado
- [x] Descarga de credenciales
- [x] Logging completo
- [x] Protección CSRF
- [x] Decorador `@admin_required`
- [x] URLs configuradas

---

**Desarrollado con ❤️ para OASIS by Senior Data Engineer & Django Expert**
