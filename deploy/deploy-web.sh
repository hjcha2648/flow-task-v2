#!/usr/bin/env bash
# Web 서버(Nginx)에 정적 파일과 사이트 설정을 배포한다. 프런트엔드를 고친 뒤에도 다시 실행한다.
# 실행: sudo bash deploy/deploy-web.sh
# /var/www/task-flow 안의 파일만 frontend/와 같게 맞추며, 다른 경로는 지우지 않는다.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WEB_ROOT=/var/www/task-flow
SITE=/etc/nginx/sites-available/task-flow

if [ "$(id -u)" -ne 0 ]; then
  echo "sudo로 실행하세요: sudo bash deploy/deploy-web.sh" >&2
  exit 1
fi

echo "1) 정적 파일 배포: $PROJECT_DIR/frontend/ → $WEB_ROOT/"
install -d -m 755 "$WEB_ROOT"
rsync -a --delete --chmod=D755,F644 --chown=root:root "$PROJECT_DIR/frontend/" "$WEB_ROOT/"

echo "2) 사이트 설정 설치: $SITE"
install -m 644 "$PROJECT_DIR/deploy/nginx-task-flow.conf" "$SITE"
ln -sf "$SITE" /etc/nginx/sites-enabled/task-flow
# 기본 사이트도 80 포트를 쓰므로 활성화 링크만 뺀다(sites-available/default 파일은 남긴다).
if [ -L /etc/nginx/sites-enabled/default ]; then
  rm /etc/nginx/sites-enabled/default
  echo "   기본 사이트 비활성화(sites-enabled/default 링크 제거)"
fi

echo "3) 설정 검사 후 적용"
nginx -t
systemctl enable --now nginx
systemctl reload nginx
echo "완료: http://127.0.0.1/"
