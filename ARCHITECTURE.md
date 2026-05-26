# ReDrive Edu - Architecture

## System Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend"]
        FE[Next.js 14<br/>React + TypeScript]
        FE --> |HTTP/REST| API
    end

    subgraph Backend["FastAPI Backend"]
        API[API Gateway<br/>FastAPI + Pydantic]
        API --> Auth[Auth Service<br/>JWT/RBAC]
        API --> Docs[Document Service<br/>Upload & Process]
        API --> Chat[RAG Service<br/>Chat & Query]
        API --> Eval[Evaluation Service<br/>Quiz & Grade]
        API --> Analytics[Analytics Service<br/>Metrics]
    end

    subgraph Data["Data Layer"]
        DB[(PostgreSQL<br/>SQLAlchemy 2.x)]
        Cache[(Redis<br/>Cache & Queue)]
        Vectors[(ChromaDB<br/>Vectors)]
    end

    subgraph Workers["Async Workers"]
        CW[Celery Workers<br/>Embeddings & OCR]
    end

    API <--> DB
    API <--> Cache
    API <--> Vectors
    CW --> |Background| Docs
    CW --> |Background| Vectors
```

## Multi-Tenant Architecture

```mermaid
graph LR
    subgraph Tenants["Multi-Tenant Isolation"]
        T1[Tenant 1<br/>Academy A]
        T2[Tenant 2<br/>Academy B]
        T3[Tenant N<br/>Academy N]
    end

    subgraph Shared["Shared Infrastructure"]
        API2[FastAPI]
        DB2[(PostgreSQL)]
        VEC[(ChromaDB)]
    end

    T1 --> |tenant_id| API2
    T2 --> |tenant_id| API2
    T3 --> |tenant_id| API2

    T1 --> |tenant_a collection| VEC
    T2 --> |tenant_b collection| VEC
    T3 --> |tenant_n collection| VEC

    API2 --> DB2
    API2 --> VEC
```

## Document Processing Pipeline

```mermaid
flowchart TD
    Upload[Document Upload<br/>PDF/DOCX/TXT]
    Validate[Validate File<br/>Size & Format]
    Extract[Extract Text<br/>OCR if needed]
    Chunk[Semantic Chunking<br/>Configurable size]
    Embed[Generate Embeddings<br/>OpenAI text-embedding-3-small]
    Store[(ChromaDB<br/>With metadata)]
    Index[Index Complete<br/>Ready for RAG]

    Upload --> Validate
    Validate --> |Valid| Extract
    Validate --> |Invalid| Error[Error Response]
    Extract --> Chunk
    Chunk --> Embed
    Embed --> Store
    Store --> Index

    Upload --> |Async| Celery[Celery Worker]
    Celery --> Extract
```

## RAG Query Flow

```mermaid
sequenceDiagram
    participant User
    participant FE as Frontend
    participant API as FastAPI
    participant RAG as RAG Engine
    participant Chroma as ChromaDB
    participant LLM as OpenAI GPT-4o-mini

    User->>FE: Ask question
    FE->>API: POST /api/v1/chat/query
    API->>Chroma: Search similar chunks
    Chroma-->>API: Relevant context
    API->>LLM: Query + Context
    LLM-->>API: Answer with citations
    API-->>FE: Response + Sources
    FE-->>User: Display with citations
```

## User Roles & Permissions

```mermaid
graph TD
    subgraph Roles["Role-Based Access Control"]
        SA[superadmin<br/>Platform Admin]
        AA[academy_admin<br/>Academy Admin]
        T[teacher<br/>Professor]
        S[student<br/>Student]
        P[parent<br/>Parent]
    end

    SA --> |Manage All| AA
    AA --> |Manage| T
    AA --> |Manage| S
    AA --> |Manage| P
    T --> |Create| Docs[Documents]
    T --> |Create| Eval[Evaluations]
    T --> |View| Analytics[Analytics]
    S --> |Take| Eval
    S --> |Chat| Chat[RAG Chat]
    P --> |View| Progress[Student Progress]
```

## Deployment Architecture

```mermaid
graph TB
    subgraph Cloud["Cloud Deployment"]
        LB[Load Balancer<br/>Railway/Fly.io]
        BE[Backend<br/>FastAPI Container]
        FE[Frontend<br/>Next.js Vercel]
        DB[(PostgreSQL<br/>Managed DB)]
        RD[(Redis<br/>Upstash/Managed)]
        CH[(ChromaDB<br/>Self-hosted)]
    end

    LB --> BE
    LB --> FE
    BE --> DB
    BE --> RD
    BE --> CH
```

## Database Schema

```mermaid
erDiagram
    TENANT {
        uuid id PK
        string name
        string slug
        string status
        timestamp created_at
    }

    USER {
        uuid id PK
        uuid tenant_id FK
        string email
        string password_hash
        string role
        string first_name
        string last_name
        boolean is_active
        timestamp created_at
    }

    DOCUMENT {
        uuid id PK
        uuid tenant_id FK
        string title
        string file_path
        string status
        int chunk_count
        timestamp created_at
    }

    CHAT_SESSION {
        uuid id PK
        uuid tenant_id FK
        uuid user_id FK
        string title
        boolean is_archived
        timestamp created_at
    }

    CHAT_MESSAGE {
        uuid id PK
        uuid session_id FK
        string role
        string content
        json citations
        int tokens_used
        timestamp created_at
    }

    EVALUATION {
        uuid id PK
        uuid tenant_id FK
        uuid document_id FK
        string title
        string evaluation_type
        int question_count
        boolean is_published
        timestamp created_at
    }

    ATTEMPT {
        uuid id PK
        uuid evaluation_id FK
        uuid user_id FK
        timestamp started_at
        timestamp completed_at
        float score
        boolean passed
    }

    TENANT ||--o{ USER : has
    TENANT ||--o{ DOCUMENT : has
    TENANT ||--o{ CHAT_SESSION : has
    USER ||--o{ CHAT_SESSION : creates
    CHAT_SESSION ||--o{ CHAT_MESSAGE : contains
    DOCUMENT ||--o{ EVALUATION : generates
    USER ||--o{ ATTEMPT : makes
    EVALUATION ||--o{ ATTEMPT : receives
```

## API Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant FE as Frontend
    participant API as FastAPI
    participant Redis as Redis

    User->>FE: Login credentials
    FE->>API: POST /auth/login
    API->>API: Validate credentials
    API->>API: Generate JWT tokens
    API->>Redis: Store refresh token
    API-->>FE: access_token + refresh_token
    FE-->>User: Login success

    Note over User,FE: Subsequent requests
    FE->>API: Request + access_token
    API-->>FE: Response
    API->>API: Check token expiry
```

## Technology Stack

```mermaid
graph LR
    subgraph Frontend["Frontend"]
        TS[TypeScript]
        NX[Next.js 14]
        TW[Tailwind CSS]
        RQ[TanStack Query]
        ZU[Zustand]
    end

    subgraph Backend["Backend"]
        FA[FastAPI]
        PY[Python 3.11]
        SA[SQLAlchemy 2.x]
        PD[Pydantic v2]
    end

    subgraph AI["AI/ML"]
        LLM[OpenAI GPT-4o-mini]
        EMB[text-embedding-3-small]
        RI[LlamaIndex]
        CB[ChromaDB]
    end

    subgraph Infra["Infrastructure"]
        PG[PostgreSQL]
        RD[Redis]
        CL[Celery]
        DK[Docker]
    end

    NX --> TS
    FA --> PY
    SA --> PG
    LLM --> EMB
    RI --> CB
```

## Performance Metrics

```mermaid
gantt
    title Request Latency Targets
    dateFormat X
    axisFormat %s

    section API
    Simple API call :0, 300
    RAG Query (no streaming) :0, 2000
    RAG Streaming start :0, 500

    section Processing
    50-page PDF processing :0, 30000
    Embedding generation :0, 5000
```

## Monitoring & Observability

```mermaid
graph TD
    subgraph Observability
        Logs[(Structured Logs<br/>JSON)]
        Metrics[(Metrics<br/>Tokens/Latency)]
        Traces[(Traces<br/>Request IDs)]
    end

    subgraph Logging["Log Structure"]
        L1[tenant_id]
        L2[user_id]
        L3[request_id]
        L4[endpoint]
        L5[latency_ms]
        L6[status_code]
        L7[error_message]
    end

    subgraph Metrics["Key Metrics"]
        M1[Token usage]
        M2[Response latency]
        M3[Error rate]
        M4[Hallucination rate]
    end

    Logs --> Logs
    Metrics --> Metrics
    Logs --> L1
    Logs --> L2
    Logs --> L3
    Logs --> L4
    Logs --> L5
    Logs --> L6
    Logs --> L7
    Metrics --> M1
    Metrics --> M2
    Metrics --> M3
    Metrics --> M4
```