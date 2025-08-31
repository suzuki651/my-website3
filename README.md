Flask お問い合わせ管理システム
このリポジトリは、PythonのWebフレームワークであるFlaskを使用して開発された、お問い合わせフォームと管理者向け管理画面を備えたWebアプリケーションです。

🚀 アプリケーションの機能
お問い合わせフォーム: ユーザーからの問い合わせを受け付け、データベースに保存します。

管理者ログイン: 管理者のみがアクセスできる安全なログインページを提供します。

お問い合わせ管理: 管理者はお問い合わせ内容の一覧表示、詳細確認が可能です。

パスワードリセット: 登録されたメールアドレスとセキュリティ質問を利用してパスワードをリセットできます。

メール通知機能: パスワードリセット時などに自動でメールを送信します。

データベース: 軽量なSQLite3を使用し、Azure App Serviceなどのクラウド環境にも簡単にデプロイできます。

🛠️ 環境構築と実行方法
1. リポジトリのクローン
Bash

git clone https://github.com/your-username/your-repository.git
cd your-repository
2. 仮想環境の作成とアクティベート
Bash

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
3. 必要なライブラリのインストール
Bash

pip install -r requirements.txt
4. 環境変数の設定
プロジェクトのルートディレクトリに .env ファイルを作成し、以下の内容を記述します。

コード スニペット

FLASK_ENV=development
SECRET_KEY='your-strong-secret-key'

# メール設定（Gmailの例）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER='your-email@gmail.com'
EMAIL_PASSWORD='your-16-digit-app-password'
EMAIL_FROM='your-email@gmail.com'
SECRET_KEY: セッション管理のために必須です。予測不可能なランダムな文字列に設定してください。

EMAIL_PASSWORD: Googleアカウントのアプリパスワードを生成し、16桁のパスワードを設定します。

5. アプリケーションの実行
Bash

python app.py
アプリケーションは http://127.0.0.1:5000 で起動します。

🔐 管理者アカウント情報
アプリケーションを初めて実行すると、データベースにデフォルトの管理者アカウントが作成されます。

項目	値
ユーザー名	admin
パスワード	admin1q2w3e
セキュリティ質問の答え	pet

Google スプレッドシートにエクスポート
🚨 重要: サービスを公開する前に、これらのデフォルト情報を必ず変更してください。

🔗 主なURL
一般向けページ
/: トップページ

/about: サービス紹介

/access: お問い合わせフォーム

管理者向けページ
/admin/login: 管理者ログイン

/admin/: ダッシュボード

/admin/contacts: お問い合わせ一覧

/admin/forgot-password: パスワードリセット要求