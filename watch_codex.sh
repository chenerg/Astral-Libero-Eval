#!/usr/bin/env bash
# Wake only on terminal events for the Astra-LIBERO episode.
set -euo pipefail
PID="${1:?codex pid}"
ROOT="/home/chener/LIBERO/astra_eval"
RESULT="$ROOT/runs/current/result.json"
LOG="$ROOT/logs/codex.log"
diag="$ROOT/logs/watch_$PID.log"

codex_alive() { kill -0 "$PID" 2>/dev/null; }
has_result() { [[ -f "$RESULT" ]]; }

while :; do
  if has_result; then
    echo "DONE: episode result written $(python3 -c "import json; d=json.load(open('$RESULT')); print('success='+str(d.get('success')), d.get('reason'), 'moves='+str(d.get('moves')), 'steps='+str(d.get('env_steps')))" 2>/dev/null || echo $RESULT)"
    exit 0
  fi
  if ! codex_alive; then
    if has_result; then
      echo "DONE: Codex exited and result exists"
      exit 0
    fi
    echo "FAILED: Codex pid $PID exited without result.json"
    tail -40 "$LOG" | tr '\n' ' ' >>"$diag" || true
    echo "FAILED: last log: $(tail -c 400 "$LOG" 2>/dev/null | tr '\n' ' ')"
    exit 1
  fi
  sleep 15
done
