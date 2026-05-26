#!/usr/bin/env bash

BASE_URL="https://c3po-production.up.railway.app"

CANDIDATES=(
  "/api/v1/auth/login"
  "/api/v1/login"
  "/api/v1/users/login"
  "/api/v1/auth/token"
  "/auth/login"
  "/login"
)

echo "Probando rutas contra: $BASE_URL"
echo "-------------------------------------"

for path in "${CANDIDATES[@]}"; do
  url="${BASE_URL}${path}"
  status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$url")
  echo "$status  ->  $url"
done
