#!/bin/bash

# 起動スクリプト for Azure App Service
# ファイル名: start.sh

set -e  # エラー時に停止

echo "🚀 Azure App Service でアプリケーションを起動中..."

# 環境変数の設定
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# ログ出力の設定
export PYTHONUNBUFFERED=1

# Azure App Service の動的ポート対応
if [ -n "$PORT" ]; then
    BIND_PORT=$PORT
else
    BIND_PORT=8000
fi

echo "📊 環境情報:"
echo "  - Python version: $(python --version)"
echo "  - Working directory: $(pwd)"
echo "  - Port: $BIND_PORT"
echo "  - FLASK_ENV: $FLASK_ENV"

# データディレクトリを作成
echo "📁 データディレクトリを作成中..."
mkdir -p /home/data
mkdir -p /home/LogFiles

# 依存関係の確認
echo "📦 依存関係の確認:"
python -c "import flask, gunicorn; print(f'Flask: {flask.__version__}, Gunicorn: {gunicorn.__version__}')"

# データベースの初期化（事前チェック）
echo "🗄️  データベース初期化チェック..."
python -c "from app import init_db; init_db(); print('✅ データベース初期化完了')" || {
    echo "⚠️  データベース初期化で警告が発生しましたが、継続します"
}

# Gunicornでアプリケーションを起動
echo "🌟 Gunicornでアプリケーションを起動中..."
exec gunicorn \
    --bind "0.0.0.0:$BIND_PORT" \
    --workers 2 \
    --worker-class sync \
    --worker-connections 1000 \
    --timeout 120 \
    --keepalive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    app:app