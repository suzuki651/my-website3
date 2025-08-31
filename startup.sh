#!/bin/bash

# Azureの環境変数を設定
export FLASK_ENV=production

# データディレクトリを作成
mkdir -p /home/data

# Gunicornでアプリケーションを起動
gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 --preload app:app