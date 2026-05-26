# ReDrive Edu - Frontend

Frontend para la plataforma de tutoría académica con IA.

## Stack Tecnológico

- **Framework**: Next.js 14 (App Router)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS
- **State Management**: Zustand + TanStack Query
- **UI Components**: Custom + Radix UI primitives
- **Formularios**: React Hook Form + Zod
- **Gráficos**: Recharts
- **Notificaciones**: Sonner

## Requisitos

- Node.js 18+
- npm o yarn

## Instalación

```bash
# Instalar dependencias
npm install

# Copiar archivo de configuración
cp .env.example .env.local

# Editar .env.local con tu configuración
```

## Variables de Entorno

```env
# URL del backend (default: http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000

# URL de esta aplicación
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Desarrollo

```bash
# Iniciar servidor de desarrollo
npm run dev

# Construir para producción
npm run build

# Iniciar producción
npm start
```

## Estructura del Proyecto

```
src/
├── app/                    # Next.js App Router
│   ├── auth/              # Páginas de autenticación
│   ├── dashboard/        # Dashboard principal
│   ├── chat/             # Interfaz de chat RAG
│   ├── documents/        # Gestor de documentos
│   ├── evaluations/      # Módulo de evaluaciones
│   └── analytics/       # Dashboard de analíticas
├── components/           # Componentes reutilizables
├── lib/                  # Utilidades y configuración
│   ├── api.ts           # Cliente API con interceptores
│   ├── store.ts         # Estado global (Zustand)
│   └── utils.ts         # Funciones auxiliares
├── services/             # Servicios de API
│   ├── auth.service.ts
│   ├── document.service.ts
│   ├── chat.service.ts
│   ├── evaluation.service.ts
│   └── analytics.service.ts
├── types/               # Tipos TypeScript
└── styles/             # Estilos globales
```

## Funcionalidades

### Autenticación
- Login con email y contraseña
- Registro de nuevos usuarios
- JWT con refresh token automático
- Roles: superadmin, academy_admin, teacher, student, parent

### Chat RAG
- Interfaz conversacional con IA
- Respuestas citadas de documentos
- Streaming de respuestas
- Historial de conversaciones

### Documentos
- Subida de archivos (PDF, DOCX, TXT, MD)
- Estado de procesamiento
- Listado y eliminación

### Evaluaciones
- Realización de quizzes
- Corrección automática
- Feedback detallado
- Historial de resultados

### Analíticas
- Métricas de uso
- Gráficos de rendimiento
- Progreso por estudiante

## Testing

```bash
# Ejecutar tests
npm test

# Tests con coverage
npm run test:coverage

# Modo watch
npm run test:watch
```

## Diseño

El diseño sigue estos principios:
- UI limpia y moderna
- Microinteracciones y animaciones suaves
- Responsive (desktop, tablet, móvil)
- Tema claro/oscuro

## Conexión con Backend

El frontend está preparado para conectarse al backend de ReDrive Edu:

- **Auth**: JWT tokens en cookies
- **Tenant**: Header `X-Tenant-ID` en todas las requests
- **Streaming**: SSE para respuestas de chat
- **Upload**: multipart/form-data con progreso

Ver documentación del backend para más detalles de la API.