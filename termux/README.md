# C3PO - Termux (Android)

Ejecuta C3PO en tu dispositivo Android usando Termux.

## Requisitos

- **Termux** instalado desde [F-Droid](https://f-droid.org/en/packages/com.termux/) o [GitHub](https://github.com/termux/termux-app/releases)
- Android 7.0 o superior
- Al menos 2GB de almacenamiento libre
- Conexión a internet para descargar dependencias

## Instalación Rápida

```bash
# 1. Clona el proyecto
git clone https://github.com/Oppenheimmer-droid/c3po.git

# 2. Entra al directorio termux
cd c3po/termux

# 3. Ejecuta el script de instalación
bash setup.sh

# 4. Configura tu API Key de Groq
nano ../backend/.env
# Edita: GROQ_API_KEY=gsk_tu_key_real

# 5. Inicializa la base de datos
bash init-db.sh

# 6. ¡Inicia C3PO!
bash start.sh

# 7. Abre http://localhost:3000 en tu navegador
```

## Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `setup.sh` | Instala todas las dependencias y configura el entorno |
| `init-db.sh` | Inicializa PostgreSQL y crea las tablas de la BD |
| `start.sh` | Inicia todos los servicios (PostgreSQL, Redis, Backend, Frontend) |
| `stop.sh` | Detiene todos los servicios |
| `status.sh` | Muestra el estado de todos los servicios |

## Estructura de Puertos

| Servicio | Puerto | URL |
|----------|--------|-----|
| Frontend (Next.js) | 3000 | http://localhost:3000 |
| Backend (FastAPI) | 8000 | http://localhost:8000 |
| API Docs (Swagger) | 8000 | http://localhost:8000/docs |

## Primeros Pasos

### 1. Obtener API Key de Groq

1. Ve a [console.groq.com](https://console.groq.com)
2. Crea una cuenta o inicia sesión
3. Genera una nueva API Key
4. Edita `backend/.env` y configura tu key:

```bash
nano ../backend/.env
```

Cambia:
```
GROQ_API_KEY=gsk_tu_key_real
```

### 2. Verificar la Instalación

```bash
# Ver estado de servicios
bash status.sh

# Ver logs del backend
tail -f ~/c3po-data/backend.log

# Ver logs del frontend  
tail -f ~/c3po-data/frontend.log
```

### 3. Acceder a C3PO

1. Abre tu navegador
2. Ve a: http://localhost:3000
3. Crea una cuenta o inicia sesión

## Solución de Problemas

### PostgreSQL no inicia

```bash
# Verificar estado
pg_isready

# Iniciar manualmente
pg_ctl -D ~/../usr/var/lib/postgresql start
```

### Error de conexión a BD

```bash
# Verificar que PostgreSQL está corriendo
bash status.sh

# Reiniciar PostgreSQL
pg_ctl -D ~/../usr/var/lib/postgresql restart
```

### Puerto en uso

```bash
# Ver qué está usando el puerto
lsof -i :3000
lsof -i :8000

# Matar el proceso
pkill -f "next"
pkill -f "uvicorn"
```

### Reinstalación completa

```bash
# Detener todo
bash stop.sh

# Eliminar datos
rm -rf ~/c3po-data
rm -rf ~/../usr/var/lib/postgresql

# Reiniciar instalación
bash setup.sh
```

## Notas Importantes

- **No cierres Termux** mientras C3PO esté corriendo. Usa `bash stop.sh` primero.
- Para acceso desde otros dispositivos en la misma red, usa la IP de tu dispositivo.
- El almacenamiento de Termux es limitado. Considera usar una tarjeta SD.

## Comunidad

- 🌟 Dale una estrella al proyecto
- 🐛 Reporta bugs en GitHub Issues
- 💡 Contribuye con mejoras

## Licencia

MIT License - ver [LICENSE](../LICENSE) para más detalles.
