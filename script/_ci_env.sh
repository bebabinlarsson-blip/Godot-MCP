## Shared env preamble for every ``script/ci-*`` runner. Sourced from the
## top of each ci-* script via ``source "$(dirname "$0")/_ci_env.sh"``.
##
## Match the workflow ``env:`` block opt-out for telemetry: no fake
## "installs" or stray streaming-insert quota from local dev runs of
## these scripts either. The collector treats this flag as a hard
## opt-out (no UUID generated, no worker thread, no _send). See
## docs/TELEMETRY.md.
export GODOT_AI_DISABLE_TELEMETRY=true

## Every ci-* runner reaches the MCP server through this URL. The default is
## the plugin's default port; override it when the connected editor's
## ``godot_ai/http_port`` is something else — the editor log names the port
## in its ``MCP | started server ... --port N`` line. The Python runners
## (ci-game-capture-smoke, local-game-capture-diag) read the same variable.
export MCP_SERVER_URL="${MCP_SERVER_URL:-http://127.0.0.1:8000/mcp}"

ci_load_http_auth() {
  local capability
  capability=$("${PYTHON_CMD:-python}" - "$MCP_SERVER_URL" \
    "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" <<'PY'
import sys

sys.path.insert(0, sys.argv[2])
from _transport_auth import raw_capability

try:
    print(raw_capability(sys.argv[1]))
except (RuntimeError, ValueError) as exc:
    raise SystemExit(str(exc)) from None
PY
  ) || return 1
  HTTP_AUTH_CAPABILITY="$capability"
  HTTP_AUTH_HEADERS=(-H "Authorization: Bearer $capability")
  unset capability
}
