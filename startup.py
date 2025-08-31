#!/usr/bin/env python3
"""
Azure App Service用の起動ファイル
Gunicornとの互換性を考慮した設定
"""

import os
import sys
import logging
from pathlib import Path

# Azure App ServiceのPython環境設定
IS_AZURE = 'WEBSITE_SITE_NAME' in os.environ

if IS_AZURE:
    # Azure環境での設定
    os.environ['FLASK_ENV'] = 'production'
    
    # ログディレクトリの確保
    log_dir = Path('/home/LogFiles')
    log_dir.mkdir(exist_ok=True)
    
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/home/LogFiles/application.log', encoding='utf-8')
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Azure App Service環境で起動中...")
else:
    # ローカル開発環境
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("ローカル開発環境で起動中...")

# アプリケーションをインポート
try:
    from app import app, init_db
    logger.info("アプリケーションのインポート完了")
except ImportError as e:
    logger.error(f"アプリケーションのインポートに失敗: {e}")
    raise

# データベースの初期化
def initialize_database():
    """データベースの初期化とエラーハンドリング"""
    try:
        init_db()
        logger.info("✅ データベース初期化完了")
        return True
    except Exception as e:
        logger.error(f"❌ データベース初期化エラー: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# アプリケーション起動前の初期化
if not initialize_database():
    logger.warning("データベースの初期化に失敗しましたが、アプリケーションを起動します")

# Gunicorn用のアプリケーションオブジェクト
# 本番環境（Azure + Gunicorn）では、これが使用されます
application = app

# Flask開発サーバー用（ローカル開発時のみ）
if __name__ == '__main__':
    if IS_AZURE:
        # Azure App Serviceでは通常Gunicornが使用されるため、
        # このブロックは実行されません
        logger.warning("Azure環境でFlask開発サーバーが起動されています（非推奨）")
    
    # ポート設定（Azure App Serviceの場合は HTTP_PLATFORM_PORT を使用）
    port = int(os.environ.get('HTTP_PLATFORM_PORT', os.environ.get('PORT', 8000)))
    
    logger.info(f"Flask開発サーバーを起動: ポート {port}")
    app.run(host='0.0.0.0', port=port, debug=not IS_AZURE)