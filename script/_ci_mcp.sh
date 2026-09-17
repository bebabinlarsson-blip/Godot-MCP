# Shared MCP session lifetime. Source after SERVER_URL and HEADERS are set.
# Call in the parent shell so SESSION_ID survives; callers own their EXIT trap.
close_mcp_session() {
  if [ -z "$SESSION_ID" ]; then
    return
  fi
  curl -fsS --connect-timeout 3 --max-time 10 "$SERVER_URL" -X DELETE "${HEADERS[@]}" \
    -H "Mcp-Session-Id: $SESSION_ID" > /dev/null 2>&1 || true
  SESSION_ID=""
}

initialize_mcp_session() {
  local response
  local new_session_id
  if ! response=$(curl -fsiS --connect-timeout 3 --max-time 10 \
    "$SERVER_URL" -X POST "${HEADERS[@]}" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"ci","version":"1.0"}}}'); then
    return 1
  fi
  new_session_id=$(printf '%s\n' "$response" | tr -d '\r' | awk '
    tolower($1) == "mcp-session-id:" {
      print $2
      exit
    }
  ')
  if [ -z "$new_session_id" ]; then
    return 1
  fi
  SESSION_ID="$new_session_id"
  if ! curl -fsS --connect-timeout 3 --max-time 10 \
    "$SERVER_URL" -X POST "${HEADERS[@]}" \
    -H "Mcp-Session-Id: $SESSION_ID" \
    -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' > /dev/null; then
    close_mcp_session
    return 1
  fi
}

