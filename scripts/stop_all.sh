#!/usr/bin/env bash
# LawDesign 一键停止脚本
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOGDIR="$ROOT/logs"
if ls "$LOGDIR"/*.pid >/dev/null 2>&1; then
  for pidfile in "$LOGDIR"/*.pid; do
    name="$(basename "$pidfile" .pid)"
    pid="$(cat "$pidfile")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null && echo "[STOP] $name (pid $pid)"
    fi
    rm -f "$pidfile"
  done
else
  echo "没有正在运行的服务"
fi
