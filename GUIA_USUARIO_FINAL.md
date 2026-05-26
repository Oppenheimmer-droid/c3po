# 🏫 Guía de Usuario Final - ReDrive Edu

**Plataforma de tutoría académica con inteligencia artificial**

> ⚠️ **IMPORTANTE**: Esta guía está diseñada para usuarios sin conocimientos técnicos. Si sigues los pasos en orden, el proyecto estará funcionando en menos de 10 minutos.

---

## 📋 Índice

1. [¿Qué es ReDrive Edu?](#¿qué-es-redrive-edu)
2. [Requisitos previos](#requisitos-previos)
3. [Instalación paso a paso](#instalación-paso-a-paso)
4. [Primeros pasos en la aplicación](#primeros-pasos-en-la-aplicación)
5. [Solución de problemas](#solución-de-problemas)
6. [Cómo apagar el proyecto](#cómo-apagar-el-proyecto)

---

## 🤖 ¿Qué es ReDrive Edu?

ReDrive Edu es una plataforma educativa que te permite:

- **Subir documentos** (PDF, Word, textos) con tus materiales de clase
- **Chatear con IA** que responde basándose en tus documentos, siempre citando las fuentes
- **Crear evaluaciones** (quizzes) automáticamente a partir de tus materiales
- **Seguir el progreso** de estudiantes con analíticas detalladas

**Ejemplo de uso**: Un profesor sube un PDF de matemáticas, y luego puede preguntar al chat "¿Qué fórmulas de trigonometría hay en el tema 3?" y la IA responde exactamente qué dice el documento, indicando la página.

---

## ✅ Requisitos previos

Solo necesitas dos cosas antes de empezar:

### 1. Docker Desktop

Docker es un programa que permite ejecutar la aplicación. **Descárgalo aquí**:

- **Windows**: https://www.docker.com/products/docker-desktop/ (Descarga Docker Desktop for Windows)
- **Mac**: https://www.docker.com/products/docker-desktop/ (Descarga Docker Desktop for Mac)
- **Linux**: https://docs.docker.com/desktop/install/linux-install/

**Instalación en Windows:**
1. Haz doble clic en el archivo `.exe` descargado
2. Sigue los pasos del asistente (Siguiente → Siguiente → Finalizar)
3. Reinicia el ordenador cuando lo pida
4. Busca "Docker Desktop" en el menú de inicio y ábrelo

**Instalación en Mac:**
1. Arrastra el icono de Docker a la carpeta de Aplicaciones
2. Abre Docker desde Aplicaciones
3. Acepta los permisos que pida (contraseña de Mac)

**¿Cómo saber si está instalado?**
Abre una terminal (busca "Terminal" en tu ordinateur) y escribe:
```
docker --version
```
Si ves un número de versión (ej: "Docker version 24.0.0"), ¡está listo!

---

### 2. Clave de API de OpenAI

OpenAI es la empresa que proporciona la inteligencia artificial. Necesitas una clave gratuita para que funcione.

**Pasos para obtener la clave:**

1. **Abre tu navegador** y ve a: https://platform.openai.com/

2. **Crea una cuenta** (o inicia sesión si ya tienes):
   - Clic en "Sign up" si es la primera vez
   - Usa tu correo electrónico o cuenta de Google

3. **Verifica tu correo** (revisa tu bandeja de entrada)

4. **Consigue $5 gratis** para pruebas:
   - Ve a https://platform.openai.com/settings/organization/billing/overview
   - Clic en "Add to credit balance"
   - Selecciona $5 (es suficiente para muchos meses de uso)

5. **Crea la clave API**:
   - Ve a https://platform.openai.com/api-keys
   - Clic en "+ Create new secret key"
   - Dale un nombre (ej: "ReDrive Edu")
   - Clic en "Create secret key"
   - **⚠️ COPIA LA CLAVE AHORA** - Solo se muestra una vez

**La clave tiene este formato**: `sk-...` (empieza con `sk-` y tiene muchas letras y números)

---

## 🚀 Instalación paso a paso

### Paso 1: Descargar el proyecto

**Opción A - Descargar ZIP (recomendado para novatos):**
1. Ve al repositorio en GitHub
2. Clic en el botón verde "Code"
3. Clic en "Download ZIP"
4. Descomprime el archivo en tu Escritorio o Carpeta de Documentos
5. Abre la carpeta que descomprimiste

**Opción B - Clonar con Git (si sabes usar Git):**
```bash
git clone https://github.com/Oppenheimmer-droid/c3po.git
cd c3po
```

---

### Paso 2: Configurar las variables

1. **Abre la carpeta del proyecto**
2. **Entra en la carpeta `backend`**
3. **Busca el archivo `.env.example`** y ábrelo con el Bloc de notas
4. **Crea un nuevo archivo** llamado `.env` (sin extensión)
5. **Copia este texto**:

```env
# Database - NO MODIFICAR
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/redrive_edu
REDIS_URL=redis://redis:6379/0

# OpenAI - REEMPLAZAR con tu clave
OPENAI_API_KEY=sk-aqui-tu-clave-api

# Other settings - NO MODIFICAR
SECRET_KEY=redrive-edu-secret-key-change-in-production
CHROMA_PERSIST_DIR=/app/chroma_data
ENVIRONMENT=development
DEBUG=true
```

6. **En la línea `OPENAI_API_KEY=`**, reemplaza `sk-aqui-tu-clave-api` con tu clave real de OpenAI (ej: `sk-1Ab2C3D4E5F6...`)

7. **Guarda el archivo** (Archivo → Guardar)

---

### Paso 3: Abrir Docker Desktop

1. **Busca "Docker Desktop"** en tu ordenador:
   - Windows: Menú inicio → escribe "Docker Desktop"
   - Mac: Buscador → escribe "Docker"
   
2. **Abre Docker Desktop** y espera hasta que veas:
   - En Windows: El icono de Docker en la bandeja (abajo a la derecha) se pone verde
   - En Mac: La ventana de Docker indica "Docker Desktop is running"

⚠️ **Importante**: Docker debe estar corriendo ANTES de continuar.

---

### Paso 4: Levantar el proyecto

1. **Abre una terminal**:
   - Windows: Clic derecho en el menú inicio → "Terminal" o "PowerShell"
   - Mac: Aplicaciones → Utilidades → Terminal

2. **Navega a la carpeta del proyecto**:
   ```bash
   cd ~/Desktop/redrive-edu  # O la ruta donde descomprimiste
   cd backend               # Entra en la carpeta backend
   ```

3. **Ejecuta el comando** (copia y pega esto):
   ```bash
   docker-compose up
   ```

4. **Espera**... Esto puede tardar 2-5 minutos la primera vez.

5. **¿Cómo saber que está listo?** 
   - Verás texto en la terminal que dice `Ready` o `started`
   - No habrá errores rojos importantes
   - La terminal seguirá mostrando texto (está corriendo)

---

### Paso 5: Abrir la aplicación

1. **Abre tu navegador** (Chrome, Firefox, Edge, Safari)

2. **Escribe en la barra de direcciones**:
   ```
   http://localhost:3000
   ```

3. **¡Ya está!** Deberías ver la pantalla de login de ReDrive Edu.

---

## 🎓 Primeros pasos en la aplicación

### Iniciar sesión con el usuario demo

Al iniciar el proyecto, se crea automáticamente un usuario administrador:

- **Email**: `admin@redrive.edu`
- **Contraseña**: `admin123`

1. En la página de login, escribe el email y contraseña
2. Clic en "Iniciar sesión"
3. ¡Bienvenido al dashboard!

---

### Explorar el dashboard

El dashboard te muestra diferentes opciones según tu rol como administrador:

| Sección | Qué hace |
|---------|----------|
| **Chat con IA** | Pregunta cosas sobre tus documentos |
| **Documentos** | Sube y gestiona archivos |
| **Evaluaciones** | Crea quizzes y exámenes |
| **Analíticas** | Ve gráficos de progreso |

---

### Subir un documento de ejemplo

1. Clic en **"Documentos"** en el menú
2. Clic en el botón **"Subir documento"**
3. **Selecciona un PDF** de tu ordenador (máx 50MB)
4. **Escribe un título** (ej: "Apuntes de Matemáticas")
5. Clic en **"Subir"**
6. **Espera 1-2 minutos** mientras se procesa (verás una barra de progreso)

⚠️ **Nota**: El documento debe estar en formato PDF, Word (.docx) o texto (.txt).

---

### Usar el chat con IA

1. Clic en **"Chat con IA"** en el menú
2. Verás una ventana de chat
3. **Escribe una pregunta** sobre tu documento (ej: "¿Qué tema trata el documento?")
4. Presiona Enter o clic en el botón de enviar
5. **¡Espera la respuesta!** (tarda unos segundos)
6. **Verás la respuesta** con citas al final (ej: "Según página 2 del documento...")

**Ejemplos de preguntas**:
- "¿Qué se explica en el tema 1?"
- "¿Hay algún ejemplo de ecuaciones?"
- "¿Cuál es la fórmula principal?"

---

### Crear una evaluación (quiz)

1. Clic en **"Evaluaciones"** en el menú
2. Clic en **"Crear evaluación"**
3. **Selecciona el documento** que subiste antes
4. **Elige el número de preguntas** (ej: 5)
5. Clic en **"Crear"**
6. **Espera** mientras la IA genera las preguntas
7. **Publica la evaluación** cuando esté lista

---

### Ver analíticas

1. Clic en **"Analíticas"** en el menú
2. Verás gráficos de:
   - Actividad semanal
   - Rendimiento por materia
   - Distribución de calificaciones

---

## 🔧 Solución de problemas

### ❌ "Docker no arranca"

**Solución 1**: Reinicia tu ordenador y abre Docker Desktop de nuevo

**Solución 2**: Si tienes Windows, desactiva Hyper-V y vuelve a activarlo:
1. Panel de control → Programas → Activar/desactivar características de Windows
2. Desmarca "Hyper-V" → Aceptar
3. Reinicia
4. Vuelve a marcar "Hyper-V" → Aceptar
5. Reinicia de nuevo

**Solución 3**: Desinstala y vuelve a instalar Docker Desktop

---

### ❌ "Error: API key no válida"

**Causa**: La clave de OpenAI está mal escrita o incompleta.

**Solución**:
1. Abre el archivo `.env` en la carpeta `backend`
2. Verifica que `OPENAI_API_KEY=` tenga tu clave completa (empieza con `sk-`)
3. Guarda el archivo
4. Detén el proyecto (Ctrl+C en la terminal)
5. Ejecuta `docker-compose up` de nuevo

---

### ❌ "El chat no responde"

**Causa 1**: El documento todavía se está procesando.

**Solución**: Espera 1-2 minutos y actualiza la página. Verifica que el documento tenga estado "completado" en la sección de Documentos.

**Causa 2**: No has subido ningún documento.

**Solución**: Sube al menos un documento antes de usar el chat.

---

### ❌ "La página no carga"

**Solución 1**: Verifica que Docker esté corriendo (icono verde en la bandeja)

**Solución 2**: Espera más tiempo (hasta 5 minutos la primera vez)

**Solución 3**: Detén y reinicia:
1. Ctrl+C en la terminal
2. `docker-compose down`
3. `docker-compose up`

---

### ❌ "Error de conexión a base de datos"

**Solución**:
1. Detén el proyecto (Ctrl+C)
2. Elimina los contenedores: `docker-compose down -v`
3. Ejecuta `docker-compose up` de nuevo

⚠️ **Esto borra todos los datos** (como empezar de nuevo)

---

## 🛑 Cómo apagar el proyecto

### Opción 1 - Desde la terminal (recomendado):
1. Ve a la terminal donde está corriendo docker-compose
2. Presiona **Ctrl+C** (mantén presionado Ctrl y presiona C)
3. Espera a que se detenga
4. Ejecuta: `docker-compose down`

### Opción 2 - Cerrar completamente:
```bash
docker-compose down
docker-compose down -v  # Si quieres borrar los datos
```

### Apagar Docker Desktop:
1. Clic en el icono de Docker (bandeja del sistema)
2. Clic en "Quit Docker Desktop"

---

## 📞 Necesitas ayuda?

1. **Revisa la documentación técnica** en `README_TECNICO.md`
2. **Consulta los problemas comunes** arriba
3. **Contacta al soporte** si el problema persiste

---

## 🎉 ¡Listo!

Ahora puedes usar ReDrive Edu con tu equipo. Recuerda:

- 🚀 Para iniciar de nuevo: `docker-compose up` en la carpeta backend
- 📚 Los datos se guardan en Docker, no se pierden al cerrar
- 🔒 Haz backup regularmente si tienes datos importantes

---

*Versión: 1.0.0 | Última actualización: 2025*