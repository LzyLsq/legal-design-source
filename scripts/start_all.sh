#!/usr/bin/env bash
# LawDesign 一键启动脚本：启动全部后端服务
# 用法:
#   ./scripts/start_all.sh            # 启动全部服务
#   ./scripts/start_all.sh login qa   # 只启动指定服务（名称见下方 SERVICES）
# 前置条件: pip install -e .   （安装 lawdesign-shared，供各服务 import shared）
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
LOGDIR="$ROOT/logs"
mkdir -p "$LOGDIR"

# 让 `import shared` 生效（未 pip install -e . 时也能直接跑）
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

# 加载 .env（如存在）
if [ -f "$ROOT/.env" ]; then
  set -a; . "$ROOT/.env"; set +a
fi

# 格式: 名称|工作目录|启动命令|端口
SERVICES=(
  "login|services/auth|\$PY login.py|5000"
  "compliance-api|services/compliance|\$PY main.py|8000"
  "user-date|services/admin|\$PY userDate.py|5009"
  "contract-data|services/contract_data|\$PY contractData.py|5010"
  "administrator|services/admin|\$PY administrator.py|5011"
  "manager|services/manager|\$PY manager.py|8003"
  "manager-feedback|services/manager|\$PY feedback.py|5032"
  "manager-feedback-b|services/manager|\$PY feedback_b.py|5033"
  "qa|services/qa/ragtest/utils|\$PY QA.py|5002"
  "graphrag-service|services/qa/ragtest/utils|\$PY app.py|5005"
  "graphrag-api|services/qa/ragtest/utils|\$PY main.py|8012"
  "lawshow|services/lawshow|\$PY lawshow.py|5003"
  "analysis-case|services/analysis_case|\$PY kimiapi.py|5006"
  "calculate|services/calculate|\$PY caculate.py|5007"
  "sparkshow|services/spark_dashboard|\$PY show.py|5008"
  "risk-analysis|services/risk_analysis|\$PY riskanalysis.py|5020"
  "litigation-model|services/litigation|\$PY modellitigation.py|5025"
  "litigation-manage|services/litigation|\$PY managelitigation.py|5026"
  "litigation-edit|services/litigation|\$PY mymodel.py|5030"
  "litigation-feedback|services/litigation|\$PY feedback.py|5031"
  "agreement-manage|services/agreement|\$PY managelagreement.py|5027"
  "agreement-model|services/agreement|\$PY modelagreement.py|5028"
  "agreement-edit|services/agreement|\$PY mymodel.py|5029"
  "agreement-feedback|services/agreement|\$PY feedback.py|5034"
)

wait_port() {
  for _ in $(seq 1 40); do
    (echo > "/dev/tcp/127.0.0.1/$1") >/dev/null 2>&1 && return 0
    sleep 0.25
  done
  return 1
}

started=0; failed=0
for entry in "${SERVICES[@]}"; do
  IFS='|' read -r name dir cmd port <<< "$entry"
  if [ "$#" -gt 0 ] && ! printf '%s\n' "$@" | grep -qx "$name"; then continue; fi
  if lsof -i :"$port" >/dev/null 2>&1; then
    echo "[SKIP] $name (端口 $port 已被占用)"
    continue
  fi
  (
    cd "$ROOT/$dir" || exit 1
    eval "nohup $PY $cmd" > "$LOGDIR/$name.log" 2>&1 &
    echo $! > "$LOGDIR/$name.pid"
  )
  if wait_port "$port"; then
    echo "[ OK ] $name  -> http://127.0.0.1:$port"
    started=$((started+1))
  else
    echo "[FAIL] $name  (详见 logs/$name.log)"
    failed=$((failed+1))
  fi
done
echo "----------------------------------------"
echo "启动成功: $started 个, 失败: $failed 个; 日志目录: $LOGDIR"
