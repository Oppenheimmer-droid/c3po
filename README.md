# 🤖 C3PO - AI Tutor Platform

> **C3PO** es una plataforma de tutoría IA basada en RAG (Retrieval-Augmented Generation) que permite aprender cualquier tema con asistencia inteligente.

## 🚀 Inicio Rápido

### Opción 1: Script de Inicio

```bash
# Dar permisos de ejecución
chmod +x start.sh

# Ejecutar
./start.sh
```

### Opción 2: Manual

```bash
# Instalar dependencias
pip install fastapi uvicorn pydantic pydantic-settings httpx openai chromadb

# Ejecutar
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Opción 3: Docker

```bash
docker build -t c3po .
docker run -p 8000:8000 c3po
```

## 🌐 Acceso

- **UI Interactiva:** http://localhost:8000/ui
- **API:** http://localhost:8000/api/v1
- **Health:** http://localhost:8000/health

## 📚 API Endpoints

### GET /api/v1/roles
Lista todos los roles de tutor disponibles.

```bash
curl http://localhost:8000/api/v1/roles
```

### POST /api/v1/query
Envía una pregunta a un tutor específico.

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Qué es el teorema de Pitágoras?", "role": "matematicas"}'
```

## 🎓 Roles Disponibles

| Rol | Nombre | Estilo | Tono |
|-----|--------|--------|------|
| `matematicas` | Tutor de Matemáticas | Explica paso a paso | Paciente |
| `programacion` | Tutor de Programación | Ejemplos de código | Directo |
| `idiomas` | Tutor de Idiomas | Frases y correcciones | Amable |
| `ciencias` | Tutor de Ciencias | Analogías claras | Científico |
| `historia` | Tutor de Historia | Contexto y causas | Narrativo |
| `oposiciones` | Tutor de Oposiciones | Resúmenes y test | Preciso |

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `OPENAI_API_KEY` | Clave API de OpenAI | (requerido para IA completa) |
| `CHROMA_HOST` | Host de ChromaDB | localhost |
| `CHROMA_PORT` | Puerto de ChromaDB | 8000 |
| `DEBUG` | Modo debug | false |

### Ejemplo

```bash
export OPENAI_API_KEY=sk-...
uvicorn app.main:app --reload
```

## 🏗️ Arquitectura

```
┌────────────────────────────────────────┐
│              Frontend                  │
│         (HTML + JavaScript)            │
│         Puerto: 3000 (o /ui)           │
└──────────────┬─────────────────────────┘
               │ REST API
               ▼
┌────────────────────────────────────────┐
│           FastAPI Backend              │
│              Puerto: 8000              │
├────────────────────────────────────────┤
│  /query  →  RAG Pipeline               │
│  /roles  →  Role Definitions          │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        ▼               ▼
  ┌───────────┐   ┌───────────┐
  │ ChromaDB  │   │  OpenAI   │
  │ (Vectores)│   │   (LLM)   │
  └───────────┘   └───────────┘
```

## 📁 Estructura del Proyecto

```
c3po/
├── app/
│   ├── main.py           # Aplicación FastAPI
│   ├── api/
│   │   └── roles.py      # Endpoints de roles
│   ├── core/
│   │   ├── roles.py      # Definiciones de roles
│   │   └── settings.py   # Configuración
│   └── services/
│       ├── rag_pipeline.py    # Pipeline RAG
│       ├── embeddings.py      # OpenAI embeddings
│       ├── chroma_client.py   # Cliente ChromaDB
│       └── chunking.py        # Chunking de texto
├── index.html            # Frontend UI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── start.sh             # Script de inicio
```

## 🔒 Modo Offline

Si no se configura `OPENAI_API_KEY`, el sistema funciona en **modo offline**:
- Las respuestas indican que se necesita la clave API
- El frontend sigue siendo funcional
- ChromaDB también puede estar offline

## 🐳 Docker Compose

Para levantar toda la infraestructura:

```bash
docker-compose up -d
```

Esto levanta:
- **ChromaDB** en puerto 8001
- **API** en puerto 8000

## 📊 Schema de Respuestas

### Respuesta de /query

```json
{
  "query": "¿Qué es una ecuación cuadrática?",
  "role": "matematicas",
  "answer": "Una ecuación cuadrática es...",
  "context_used": true
}
```

### Respuesta de /roles

```json
{
  "roles": [
    {
      "id": "matematicas",
      "name": "Tutor de Matemáticas",
      "style": "Explica paso a paso.",
      "tone": "Paciente."
    }
  ]
}
```

## 📄 Licencia

MIT License - 2024