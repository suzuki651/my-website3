import os
import sys

# Azure App ServiceのPython環境設定
if 'WEBSITE_SITE_NAME' in os.environ:
    # Azure環境での設定
    os.environ['FLASK_ENV'] = 'production'
    
    # ログ設定
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/home/LogFiles/application.log')
        ]
    )

# アプリケーションをインポート
from app import app, init_db

# データベースの初期化
try:
    init_db()
    print("データベース初期化完了")
except Exception as e:
    print(f"データベース初期化エラー: {e}")
    import traceback
    traceback.print_exc()

if __name__ == '__main__':
    # Azure App Serviceから呼び出される場合
    port = int(os.environ.get('HTTP_PLATFORM_PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)