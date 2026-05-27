#!/usr/bin/env bash

# ============================
#  CONFIG
# ============================
CHROMA_HOST="https://chroma-production-628b.up.railway.app"
CHROMA_PORT="8000"
COLLECTION="knowledge_base"

# ============================
#  HEARTBEAT
# ============================
heartbeat() {
  echo "→ Heartbeat:"
  curl -s "${CHROMA_HOST}/api/v2/heartbeat" | jq .
}

# ============================
#  CREATE COLLECTION
# ============================
create_collection() {
  echo "→ Creating collection: $COLLECTION"

  curl -s -X POST "${CHROMA_HOST}/api/v2/collections" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"${COLLECTION}\",
      \"metadata\": {\"hnsw:space\": \"cosine\"}
    }" | jq .
}

# ============================
#  ADD DOCUMENTS
# ============================
add_docs() {
  echo "→ Adding documents to: $COLLECTION"

  curl -s -X POST "${CHROMA_HOST}/api/v2/collections/${COLLECTION}/add" \
    -H "Content-Type: application/json" \
    -d "{
      \"ids\": [\"doc1\", \"doc2\"],
      \"documents\": [
        \"Este es el primer documento de prueba.\",
        \"Este es el segundo documento para RAG.\"
      ],
      \"metadatas\": [
        {\"source\": \"manual\"},
        {\"source\": \"faq\"}
      ]
    }" | jq .
}

# ============================
#  QUERY DOCUMENTS
# ============================
query_docs() {
  QUERY="$1"
  echo "→ Query: $QUERY"

  curl -s -X POST "${CHROMA_HOST}/api/v2/collections/${COLLECTION}/query" \
    -H "Content-Type: application/json" \
    -d "{
      \"query_texts\": [\"${QUERY}\"],
      \"n_results\": 3
    }" | jq .
}

# ============================
#  MENU
# ============================
case "$1" in
  heartbeat)
    heartbeat
    ;;
  create)
    create_collection
    ;;
  add)
    add_docs
    ;;
  query)
    query_docs "$2"
    ;;
  *)
    echo "Uso:"
    echo "  ./chroma_client.sh heartbeat"
    echo "  ./chroma_client.sh create"
    echo "  ./chroma_client.sh add"
    echo "  ./chroma_client.sh query \"tu pregunta\""
    ;;
esac
