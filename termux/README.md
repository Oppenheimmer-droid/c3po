# 📱 C3PO EdTech Platform - Termux Edition v2.1.0

<p align="center">
  <img src="https://img.shields.io/badge/Termux-Android-000?logo=android" alt="Termux">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Node.js-20+-green?logo=node.js" alt="Node.js">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-red?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-14.2+-black?logo=next.js" alt="Next.js">
</p>

> **C3PO completo en tu bolsillo** - La plataforma educativa de IA funcionando en tu Android con Termux.

## 🎯 Descripción

C3PO EdTech Platform es una plataforma educativa con tutoría IA integrada. Esta versión está optimizada para ejecutarse completamente en **Termux (Android)** sin necesidad de root, permitiéndote tener un entorno de desarrollo completo en tu dispositivo móvil.

## ✨ Características

- 🤖 **Tutor IA con Groq** - Asistencia educativa con IA gratuita (Groq)
- 📚 **Gestión de Materias** - Organiza contenido educativo
- 📋 **Evaluaciones Automatizadas** - Genera quizzes con IA
- 💬 **Chat Interactivo** - Conversaciones con contexto RAG
- 👥 **Multi-tenant** - Soporte para múltiples instituciones
- 📊 **Dashboard Analítico** - Estadísticas y progreso

## 📋 Requisitos

| Requisito | Mínimo | Recomendado |
|-----------|--------|-------------|
| Android | 7.0 (API 24) | 10+ (API 29) |
| Almacenamiento | 1.5 GB | 3 GB |
| RAM | 2 GB | 4 GB |
| Terminal | Termux (F-Droid) | Última versión |

> ⚠️ **IMPORTANTE**: Descarga Termux desde [F-Droid](https://f-droid.org/packages/com.termux/) (no desde Google Play, ya que está desactualizado)

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática Completa

```bash
# 1. Clonar o copiar este directorio a tu teléfono
#    (usando Termux: share from Files app → Termux)
#    O desde PC: scp -r ./termux termux@ip:~/

# 2. En Termux, ir al directorio
cd ~/c3po-termux

# 3. Ejecutar instalación (primera vez, ~15-20 min)
bash setup.sh

# 4. Configurar API Key de Groq
nano backend/.env
# Editar: GROQ_API_KEY=gsk_tu_key_real

# 5. Inicializar base de datos
bash init-db.sh

# 6. ¡Listo! Iniciar servicios
bash start.sh
```

### Opción 2: Instalación Manual

```bash
# Instalar paquetes base
pkg update && pkg upgrade
pkg install -y git python python-pip nodejs npm postgresql redis

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend  
cd ../frontend
npm install

# Continuar desde paso 4 de arriba
```

## 📁 Estructura del Proyecto

```
c3po-termux/
├── setup.sh              # 🔧 Script de instalación completa
├── start.sh              # 🚀 Iniciar todos los servicios
├── init-db.sh            # 💾 Inicializar base de datos
├── README.md             # 📖 Este archivo
│
├── backend/              # ⚙️ API Backend (FastAPI)
│   ├── app/              #    Código de la aplicación
│   ├── venv/             #    Entorno virtual Python
│   ├── requirements.txt  #    Dependencias Python
│   ├── init_db.py        #    Script de inicialización
│   ├── seed_data.py      #    Datos de prueba
│   └── .env              #    Variables de entorno
│
└── frontend/             # 🌐 Frontend (Next.js)
    ├── src/              #    Código fuente React
    ├── package.json       #    Dependencias Node
    └── .env.local        #    Variables de entorno
```

## 🎮 Scripts Disponibles

| Script | Descripción | Uso |
|--------|-------------|-----|
| `setup.sh` | Instalación completa | Solo primera vez |
| `start.sh` | Iniciar todos los servicios | `bash start.sh` |
| `init-db.sh` | Reinicializar BD | `bash init-db.sh` |

## 🌐 Acceso

Una vez iniciado con `bash start.sh`:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:3000 | Aplicación web |
| **Backend API** | http://localhost:8000 | API REST |
| **API Docs** | http://localhost:8000/docs | Swagger UI |

### Credenciales de Prueba

| Rol | Email | Contraseña |
|-----|-------|------------|
| 👑 Admin | admin@imaginary.edu | admin123 |
| 👨‍🏫 Profesor | prof.martinez@imaginary.edu | teacher123 |
| 👨‍🏫 Profesor 2 | prof.rodriguez@imaginary.edu | teacher123 |
| 👨‍🎓 Estudiante | sofia.perez@imaginary.edu | student123 |
| 👨‍🎓 Estudiante | juan.lopez@imaginary.edu | student123 |
| 👨‍🎓 Estudiante | camila.diaz@imaginary.edu | student123 |

## 🔑 Configuración de API Keys

### Groq (✅ Recomendado - Gratuito)

1. Ve a https://console.groq.com/keys
2. Crea una cuenta gratis
3. Genera una API key
4. Edita `backend/.env`:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
   ```

### OpenAI (Opcional)

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🛠️ Comandos Útiles en Termux

### Gestión de Servicios

```bash
# Ver servicios activos
pgrep -a postgres
pgrep -a redis
pgrep -a python
pgrep -a node

# Detener servicios manualmente
pkill -f uvicorn     # Backend
pkill -f "next dev"  # Frontend
pg_ctl stop           # PostgreSQL
redis-cli shutdown     # Redis

# Reiniciar PostgreSQL
pg_ctl -D ~/.termux-postgresql restart
```

### Logs

```bash
# Ver logs en tiempo real
tail -f /tmp/backend.log   # Backend
tail -f /tmp/frontend.log  # Frontend
cat /tmp/postgres.log      # PostgreSQL

# Ver últimos errores
tail -20 /tmp/backend.log
```

### Base de Datos

```bash
# Acceder a PostgreSQL
psql -U postgres -d c3po

# Comandos útiles en psql:
#   \dt          → Ver tablas
#   \d tabla     → Ver estructura de tabla
#   SELECT * FROM users LIMIT 5; → Ver usuarios
#   \q           → Salir
```

### Reinstalación

```bash
# Reiniciar completamente
rm -rf backend/venv frontend/node_modules
bash setup.sh

# Solo backend
cd backend && rm -rf venv && python -m venv venv
source venv/bin/activate && pip install -r requirements.txt

# Solo frontend
cd frontend && rm -rf node_modules && npm install
```

## 🐛 Solución de Problemas

### PostgreSQL no inicia

```bash
# Solución 1: Reiniciar completamente
pg_ctl -D ~/.termux-postgresql stop 2>/dev/null || true
rm -rf ~/.termux-postgresql
initdb -D ~/.termux-postgresql
pg_ctl -D ~/.termux-postgresql start

# Solución 2: Verificar errores
cat ~/.termux-postgresql/log/*.log
```

### Puerto en uso

```bash
# Ver qué usa el puerto
lsof -i :8000   # Backend
lsof -i :3000   # Frontend

# Matar proceso
kill -9 <PID>
```

### Error de permisos

```bash
# En Termux, algunos comandos necesitan permisos especiales
# Verificar que estamos en Termux
echo $TERMUX_VERSION

# Reiniciar servicios
bash start.sh
```

### Problemas con Python

```bash
# Verificar versión
python --version  # Debe ser 3.11+

# Reinstalar pip
python -m pip install --upgrade pip

# Verificar instalación de un paquete
pip show fastapi
```

### "GROQ_API_KEY no configurada"

Edita `backend/.env`:
```bash
nano backend/.env
```
Busca la línea `GROQ_API_KEY=` y añade tu key real.

## 📊 Base de Datos

### Tablas Creadas

- `tenants` - Instituciones
- `users` - Usuarios (admin, teachers, students)
- `subjects` - Materias
- `topics` - Temas dentro de materias
- `documents` - Documentos subidos
- `evaluations` - Evaluaciones/Quizzes
- `evaluation_questions` - Preguntas
- `evaluation_attempts` - Intentos de estudiantes
- `chat_sessions` - Sesiones de chat
- `chat_messages` - Mensajes

### Datos de Prueba

El script `init-db.sh` crea:
- 1 Tenant (Academia Imaginary Knowledge)
- 6 Usuarios (1 admin, 2 profesores, 3 estudiantes)
- 8 Materias con temas
- 5 Evaluaciones de ejemplo
- 4 Intentos de evaluación

## 🔒 Seguridad

⚠️ **Para producción, cambia estos valores**:

```bash
# En backend/.env:
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql://user:STRONG_PASSWORD@host:5432/c3po
```

## 📱 Optimización para Dispositivos Lentos

Si el dispositivo es lento:

```bash
# Limitar recursos del frontend
cd frontend
NEXT_TELEMETRY_DISABLED=1 npm run dev -- -e 1000
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcion`)
3. Commit tus cambios (`git commit -am 'Agrega nueva función'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Crea un Pull Request

## 📄 Licencia

MIT License - Ver archivo LICENSE en el directorio raíz.

## 🙏 Créditos

- **C3PO EdTech Platform** - Plataforma educativa
- **Termux** - Emulador de terminal para Android
- **Groq** - API de IA gratuita
- **FastAPI** - Framework web Python
- **Next.js** - Framework web React

---

<p align="center">
  <strong>C3PO Termux Edition</strong><br>
  Desarrollado para educación accesible en dispositivos móviles<br>
  <em>"La IA al alcance de tu bolsillo"</em>
</p>
