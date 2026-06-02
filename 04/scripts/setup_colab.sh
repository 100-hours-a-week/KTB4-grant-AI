#!/usr/bin/env bash
set -e # 실행 중 명령어 실패시 스크립트 중단

curl -LsSf https://astral.sh/uv/install.sh | sh # uv 설치
export PATH="/root/.local/bin:$PATH" # 경로 추가

uv sync --inexact
uv pip install --python .venv/bin/python torch torchvision --torch-backend=auto

uv run python -c 'import torch; print("torch:", torch.__version__); print("cuda:", torch.cuda.is_available()); print("device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "no cuda")'