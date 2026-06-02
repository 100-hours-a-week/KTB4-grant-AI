#!/usr/bin/env bash
set -e # 실행 중 명령어 실패시 스크립트 중단

curl -LsSf https://astral.sh/uv/install.sh | sh # uv 설치
export PATH="/root/.local/bin:$PATH" # 경로 추가

uv sync --inexact
uv pip install torch torchvision --torch-backend=auto