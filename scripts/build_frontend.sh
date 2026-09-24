#!/usr/bin/env bash
# 构建前端并同步到各个 Flask 服务的 static/dist 目录。
#
# 背景：services/*/static/dist 里的 index.html 通过绝对路径 /static/dist/assets/...
# 引用打包产物，因此每个服务各存一份构建结果。本脚本负责"构建一次、分发多处"。
#
# 用法: ./scripts/build_frontend.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

if [ ! -d "$FRONTEND/node_modules" ]; then
  echo "==> 安装前端依赖"
  (cd "$FRONTEND" && (pnpm install || npm install))
fi

echo "==> 构建前端"
(cd "$FRONTEND" && (pnpm run build || npm run build))

for svc in auth compliance; do
  dest="$ROOT/services/$svc/static/dist"
  if [ ! -d "$dest" ]; then continue; fi
  echo "==> 同步到 services/$svc/static/dist"
  mkdir -p "$dest"
  # assets 由构建产物覆盖；js/ 下是手写资源，保持不动
  rm -rf "$dest/assets"
  cp -R "$FRONTEND/dist/assets" "$dest/assets"
  # index.html 中把 /assets/... 改写为 /static/dist/assets/...，适配 Flask 静态路由
  sed 's#/assets/#/static/dist/assets/#g' "$FRONTEND/dist/index.html" > "$dest/index.html"
done

echo "完成。"
