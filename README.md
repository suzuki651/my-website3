# Perch Web Application

Flaskを使用したお問い合わせ管理システムです。Azure App Serviceでのデプロイに対応しています。

## 機能

- お問い合わせフォーム
- 管理者ダッシュボード
- メール通知機能
- パスワードリセット機能
- レスポンシブデザイン

## ローカル開発環境のセットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/perch-web-app.git
cd perch-web-app
```

### 2. 仮想環境の作成と有効化

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

```bash
# .env.exampleをコピーして.envファイルを作成
cp .env.example .env

# .envファイルを編集して適切な値を設定
```

### 5. アプリケーションの起動

```bash
python app.py
```

アプリケーションは `http://localhost:5000` で利用可能です。

## Azure App Serviceへのデプロイ

### 前提条件

1. Azure アカウント
2. Azure App Service の作成
3. GitHub リポジトリの作成

### デプロイ手順

1. **Azure App Service の作成**
   - Azure Portal で新しいApp Serviceを作成
   - Runtime: Python 3.11
   - OS: Linux

2. **環境変数の設定**
   Azure Portal の「構成」→「アプリケーション設定」で以下を設定：
   ```
   SECRET_KEY=your-very-long-random-secret-key
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_FROM=your-email@gmail.com
   FLASK_ENV=production
   ```

3. **GitHub Secretsの設定**
   GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」で設定：
   - `AZURE_WEBAPP_NAME`: Azure Web Appの名前
   - `AZURE_WEBAPP_PUBLISH_PROFILE`: Azure Portalからダウンロードした発行プロファイル

4. **デプロイ**
   - mainブランチにpushすると自動的にデプロイされます

## 管理者アカウント

デフォルトの管理者アカウント：
- ユーザー名: `admin`
- パスワード: `admin1q2w3e`
- セキュリティ質問の答え: `pet`

**本番環境では必ずパスワードを変更してください。**

## ディレクトリ構成

```
perch-web-app/
├── app.py              # メインアプリケーション
├── startup.py          # Azure用エントリポイント
├── startup.sh          # 起動スクリプト
├── requirements.txt    # Python依存関係
├── web.config          # Azure IIS設定
├── .gitignore         # Git除外設定
├── .env.example       # 環境変数テンプレート
├── README.md          # このファイル
├── .github/
│   └── workflows/
│       └── deploy.yml  # GitHub Actions設定
└── templates/         # HTMLテンプレート
    ├── base.html
    ├── index.html
    ├── about.html
    ├── concept.html
    ├── product.html
    ├── machine.html
    ├── shop.html
    ├── access.html
    ├── admin/
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── contacts.html
    │   ├── contact_detail.html
    │   ├── change_password.html
    │   ├── forgot_password.html
    │   ├── reset_password.html
    │   └── test_email.html
    └── errors/
        ├── 404.html
        └── 500.html
```

## セキュリティ注意事項

1. **環境変数**: `.env`ファイルは絶対にGitにコミットしないでください
2. **SECRET_KEY**: 本番環境では強力なランダムキーを使用してください
3. **デフォルトパスワード**: 本番環境では必ずデフォルト管理者パスワードを変更してください
4. **メール設定**: Gmailを使用する場合はアプリパスワードを使用してください

## トラブルシューティング

### メール送信エラー
1. Googleアカウントで2段階認証が有効になっているか確認
2. アプリパスワードが正しく設定されているか確認
3. `EMAIL_*`環境変数が正しく設定されているか確認

### データベースエラー
1. `/home/data`ディレクトリの書き込み権限を確認
2. SQLite接続の制限を確認

### デプロイエラー
1. GitHub Secretsが正しく設定されているか確認
2. Azure App Serviceの設定を確認
3. ログを確認（Azure Portal の「ログ ストリーム」）

## ライセンス

MIT License

## サポート

問題や質問がある場合は、GitHubのIssuesページで報告してください。