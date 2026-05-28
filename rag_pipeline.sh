#!/usr/bin/env bash

# ============================================
# CONFIG
# ============================================
CHROMA_HOST="https://chroma-production-628b.up.railway.app"
CHROMA_PORT="8000"
COLLECTION="knowledge_base"

OPENAI_API_KEY="$OPENAI_API_KEY"
EMBED_MODEL="text-embedding-3-small"
CHAT_MODEL="gpt-4o-mini"

# ============================================
# 1) HEARTBEAT
# ============================================
heartbeat() {
  echo "→ Heartbeat Chroma"
  curl -s "${CHROMA_HOST}/api/v2/heartbeat" | jq .
}

# ============================================
# 2) CREAR COLECCIÓN
# ============================================
create_collection() {
  echo "→ Creando colección: $COLLECTION"

  curl -s -X POST "${CHROMA_HOST}/api/v2/collections" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"${COLLECTION}\",
      \"metadata\": {\"hnsw:space\": \"cosine\"}
    }" | jq .
}

# ============================================
# 3) CHUNKING (simple)
# ============================================
chunk_text() {
  local text="$1"
  local max=800
  local overlap=100

  echo "$text" | \
    sed 's/\r//g' | \
    awk -v max="$max" -v overlap="$overlap" '
      {
        if (length(current) + length($0) + 1 <= max) {
          current = current $0 "\n"
        } else {
          print current
          current = substr(current, length(current)-overlap) "\n" $0 "\n"
        }
      }
      END { print current }
    '
}

# ============================================
# 4) EMBEDDINGS (OpenAI)
# ============================================
embed() {
  local text="$1"

  curl -s https://api.openai.com/v1/embeddings \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d "{
      \"model\": \"${EMBED_MODEL}\",
      \"input\": \"${text}\"
    }" | jq -c '.data[0].embedding'
}

# ============================================
# 5) INDEXAR DOCUMENTO COMPLETO
# ============================================
index_document() {
  local doc_id="$1"
  local text="$2"

  echo "→ Chunking documento…"
  chunks=$(chunk_text "$text")

  i=0
  while read -r chunk; do
    [[ -z "$chunk" ]] && continue

    emb=$(embed "$chunk")

    curl -s -X POST "${CHROMA_HOST}/api/v2/collections/${COLLECTION}/add" \
      -H "Content-Type: application/json" \
      -d "{
        \"ids\": [\"${doc_id}_${i}\"],
        \"documents\": [\"${chunk//\"/\\\"}\"],
        \"embeddings\": [${emb}],
        \"metadatas\": [{\"source\": \"bash\"}]
      }" | jq .

    i=$((i+1))
  done <<< "$chunks"
}

# ============================================
# 6) RETRIEVAL
# ============================================
retrieve() {
  local query="$1"

  emb=$(embed "$query")

  curl -s -X POST "${CHROMA_HOST}/api/v2/collections/${COLLECTION}/query" \
    -H "Content-Type: application/json" \
    -d "{
      \"query_embeddings\": [${emb}],
      \"n_results\": 4
    }" | jq -r '.documents[0][]'
}

# ============================================
# 7) BUILD PROMPT
# ============================================
build_prompt() {
  local query="$1"
  local context="$2"

  cat <<EOF
Eres un asistente experto. Usa SOLO el contexto.

[CONTEXT]
${context}

[QUESTION]
${query}

Responde en español de forma clara y precisa.
EOF
}

# ============================================
# 8) GENERAR RESPUESTA RAG
# ============================================
rag() {
  local query="$1"

  echo "→ Recuperando contexto…"
  context=$(retrieve "$query")

  echo "→ Generando prompt…"
  prompt=$(build_prompt "$query" "$context")

  echo "→ Llamando a OpenAI…"
  curl -s https://api.openai.com/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d "{
      \"model\": \"${CHAT_MODEL}\",
      \"messages\": [
        {\"role\": \"system\", \"content\": \"Eres un asistente RAG útil y preciso.\"},
        {\"role\": \"user\", \"content\": \"${prompt//\"/\\\"}\"}
      ],
      \"temperature\": 0.2
    }" | jq -r '.choices[0].message.content'
}

# ============================================
# MENU
# ============================================
case "$1" in
  heartbeat) heartbeat ;;
  create) create_collection ;;
  index) index_document "$2" "$3" ;;
  retrieve) retrieve "$2" ;;
  rag) rag "$2" ;;
  *)
    echo "Uso:"
    echo "  ./rag_pipeline.sh heartbeat"
    echo "  ./rag_pipeline.sh create"
    echo "  ./rag_pipeline.sh index <doc_id> \"texto del documento\""
    echo "  ./rag_pipeline.sh retrieve \"pregunta\""
    echo "  ./rag_pipeline.sh rag \"pregunta\""
    ;;
esac
