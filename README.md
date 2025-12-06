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
プロジェクトのルートディレクトリに `.env` ファイルを作成します。
`.env.example` をコピーして編集するのが便利です。

```bash
cp .env.example .env
```

`.env` ファイルに以下の内容を記述します：

```bash
# Flask環境設定
FLASK_ENV=development
SECRET_KEY='your-strong-secret-key-here'

# メール設定（Gmailの例）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER='your-email@gmail.com'
EMAIL_PASSWORD='your-16-digit-app-password'
EMAIL_FROM='your-email@gmail.com'

# デフォルト管理者アカウント設定（初回起動時のみ使用）
DEFAULT_ADMIN_USERNAME='admin'
DEFAULT_ADMIN_PASSWORD='your-secure-password-here'
DEFAULT_ADMIN_EMAIL='admin@example.com'
DEFAULT_ADMIN_SECURITY_QUESTION='あなたの最初のペットの名前は？'
DEFAULT_ADMIN_SECURITY_ANSWER='your-answer-here'
```

**重要な設定項目:**

- `SECRET_KEY`: セッション管理のために必須です。予測不可能なランダムな文字列に設定してください。
  - 生成例: `python -c "import secrets; print(secrets.token_hex(32))"`

- `EMAIL_PASSWORD`: Googleアカウントのアプリパスワードを生成し、16桁のパスワードを設定します。
  - 生成URL: https://myaccount.google.com/apppasswords

- `DEFAULT_ADMIN_PASSWORD`: デフォルト管理者のパスワード。**必ず強力なパスワードに変更してください。**

- `DEFAULT_ADMIN_EMAIL`: 管理者のメールアドレス。パスワードリセット時に使用されます。

5. アプリケーションの実行
Bash

python app.py
アプリケーションは http://127.0.0.1:5000 で起動します。

🔐 管理者アカウント情報
アプリケーションを初めて実行すると、`.env` ファイルで設定した情報を使用して、データベースにデフォルトの管理者アカウントが自動的に作成されます。

デフォルト設定（`.env` ファイルで変更可能）:

| 項目 | 環境変数 | デフォルト値 |
|------|---------|------------|
| ユーザー名 | `DEFAULT_ADMIN_USERNAME` | admin |
| パスワード | `DEFAULT_ADMIN_PASSWORD` | change-this-password |
| メールアドレス | `DEFAULT_ADMIN_EMAIL` | admin@example.com |
| セキュリティ質問の答え | `DEFAULT_ADMIN_SECURITY_ANSWER` | your-answer-here |

🚨 **重要**:
- 本番環境では `.env` ファイルで**必ず強力なパスワード**に変更してください。
- `.env` ファイルは Git にコミットしないでください（`.gitignore` に含まれています）。
- アプリケーション起動後、管理画面からパスワードを変更することをお勧めします。

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