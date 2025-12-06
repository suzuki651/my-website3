# デプロイ手順ガイド

このドキュメントでは、Flask お問い合わせ管理システムを GitHub と Azure App Service にデプロイする手順を説明します。

## 📋 目次

1. [GitHubへのプッシュ](#githubへのプッシュ)
2. [Azureへのデプロイ](#azureへのデプロイ)
3. [環境変数の設定](#環境変数の設定)
4. [デプロイ後の確認](#デプロイ後の確認)

---

## 1. GitHubへのプッシュ

### 1.1 GitHubリポジトリの作成

1. [GitHub](https://github.com) にログイン
2. 右上の「+」から「New repository」を選択
3. リポジトリ情報を入力：
   - **Repository name**: `perch` (任意の名前)
   - **Description**: `Flask お問い合わせ管理システム`
   - **Visibility**: Private (推奨) または Public
   - **Initialize this repository**: チェックを入れない（既にローカルでリポジトリを作成済み）
4. 「Create repository」をクリック

### 1.2 リモートリポジトリの追加とプッシュ

```bash
# リモートリポジトリを追加（URLは作成したリポジトリのURLに置き換えてください）
git remote add origin https://github.com/YOUR_USERNAME/perch.git

# メインブランチ名を確認・変更（GitHub Actionsは main ブランチを使用）
git branch -M main

# GitHubにプッシュ
git push -u origin main
```

### 1.3 プッシュの確認

GitHubのリポジトリページで、すべてのファイルがアップロードされていることを確認してください。

**重要**: `.env` ファイルと `perch_database.db` はアップロードされていないことを確認してください（`.gitignore` で除外されています）。

---

## 2. Azureへのデプロイ

### 2.1 Azure App Serviceの作成

1. [Azure Portal](https://portal.azure.com) にログイン
2. 「リソースの作成」→「Web App」を選択
3. 基本設定を入力：
   - **サブスクリプション**: 使用するサブスクリプションを選択
   - **リソースグループ**: 新規作成または既存のものを選択（例: `ccc`）
   - **名前**: アプリ名を入力（例: `hp`）
   - **公開**: コード
   - **ランタイムスタック**: Python 3.11
   - **オペレーティングシステム**: Linux
   - **地域**: Japan East または お好みの地域
   - **価格プラン**: 適切なプランを選択（例: F1 (Free) または B1 (Basic)）
4. 「確認および作成」→「作成」をクリック

### 2.2 発行プロファイルのダウンロード

1. 作成したApp Serviceのページに移動
2. 左メニューから「概要」を選択
3. 上部の「発行プロファイルの取得」をクリック
4. `.PublishSettings` ファイルがダウンロードされます

### 2.3 GitHub Secretsの設定

GitHubリポジトリで環境変数とシークレットを設定します。

1. GitHubのリポジトリページで「Settings」タブをクリック
2. 左メニューから「Secrets and variables」→「Actions」を選択
3. 「New repository secret」をクリックして、以下のシークレットを追加：

#### 必須シークレット

| シークレット名 | 値 | 説明 |
|--------------|-----|------|
| `AZURE_WEBAPP_PUBLISH_PROFILE` | (発行プロファイルの内容) | ダウンロードした `.PublishSettings` ファイルの内容全体をコピー |
| `SECRET_KEY` | (ランダムな文字列) | Flaskのシークレットキー（例: `python -c "import secrets; print(secrets.token_hex(32))"` で生成） |
| `EMAIL_HOST` | `smtp.gmail.com` | メールサーバーのホスト名 |
| `EMAIL_PORT` | `587` | メールサーバーのポート |
| `EMAIL_USER` | `your-email@gmail.com` | メール送信元のメールアドレス |
| `EMAIL_PASSWORD` | `your-app-password` | Gmailアプリパスワード（16桁） |
| `EMAIL_FROM` | `your-email@gmail.com` | メール送信元として表示されるアドレス |
| `DEFAULT_ADMIN_USERNAME` | `admin` | デフォルト管理者のユーザー名 |
| `DEFAULT_ADMIN_PASSWORD` | `強力なパスワード` | デフォルト管理者のパスワード（**必ず強力なものに変更**） |
| `DEFAULT_ADMIN_EMAIL` | `admin@example.com` | デフォルト管理者のメールアドレス |
| `DEFAULT_ADMIN_SECURITY_QUESTION` | `あなたの最初のペットの名前は？` | セキュリティ質問 |
| `DEFAULT_ADMIN_SECURITY_ANSWER` | `your-answer` | セキュリティ質問の答え |

### 2.4 GitHub Actionsワークフローの設定確認

`.github/workflows/deploy.yml` ファイルで、以下の設定を確認・更新します：

```yaml
env:
  AZURE_WEBAPP_NAME: 'hp'           # ← 作成したApp Service名に変更
  PYTHON_VERSION: '3.11'
  RESOURCE_GROUP: 'ccc'             # ← 使用しているリソースグループ名に変更
```

設定を変更した場合は、コミットしてプッシュします：

```bash
git add .github/workflows/deploy.yml
git commit -m "Update Azure configuration"
git push origin main
```

### 2.5 自動デプロイの実行

`main` ブランチにプッシュすると、GitHub Actionsが自動的に実行されます。

1. GitHubリポジトリの「Actions」タブをクリック
2. 最新のワークフロー実行を確認
3. すべてのステップが緑色のチェックマークになれば成功

デプロイが完了すると、アプリケーションは以下のURLでアクセス可能になります：
```
https://YOUR_APP_NAME.azurewebsites.net
```

---

## 3. 環境変数の設定

### 3.1 Azure Portal での環境変数設定（任意）

GitHub ActionsがApp Serviceの環境変数を自動的に設定しますが、手動で確認・設定することもできます：

1. Azure Portalで App Service を開く
2. 左メニューから「構成」を選択
3. 「アプリケーション設定」タブで環境変数を確認・追加

### 3.2 重要な環境変数

以下の環境変数が正しく設定されていることを確認してください：

- `FLASK_ENV=production`
- `SECRET_KEY`（強力なランダム文字列）
- `EMAIL_*`（メール関連設定）
- `DEFAULT_ADMIN_*`（管理者アカウント設定）

---

## 4. デプロイ後の確認

### 4.1 アプリケーションの動作確認

1. ブラウザでアプリケーションURLにアクセス
   ```
   https://YOUR_APP_NAME.azurewebsites.net
   ```

2. トップページが表示されることを確認

3. 管理画面にアクセス
   ```
   https://YOUR_APP_NAME.azurewebsites.net/admin/login
   ```

4. 設定したデフォルト管理者アカウントでログイン

### 4.2 ログの確認

問題が発生した場合、以下の方法でログを確認できます：

#### Azure Portalでのログ確認

1. App Service を開く
2. 左メニューから「ログストリーム」を選択
3. リアルタイムでログを確認

#### SSH接続でのログ確認

1. App Service を開く
2. 左メニューから「SSH」を選択
3. 「移動」をクリック
4. 以下のコマンドでログを確認：
   ```bash
   cd /home/LogFiles
   cat application.log
   ```

### 4.3 データベースの確認

1. SSH接続でApp Serviceに接続
2. データベースファイルの確認：
   ```bash
   ls -lh /home/perch_database.db
   ```

3. 管理者アカウントの確認（Pythonを使用）：
   ```bash
   python3 -c "import sqlite3; conn = sqlite3.connect('/home/perch_database.db'); cursor = conn.cursor(); cursor.execute('SELECT username, email FROM admin_users'); print(cursor.fetchall()); conn.close()"
   ```

---

## 5. トラブルシューティング

### 5.1 アプリケーションが起動しない

- Azure Portalの「ログストリーム」でエラーメッセージを確認
- 環境変数が正しく設定されているか確認
- `web.confing` ファイルが正しくアップロードされているか確認

### 5.2 管理者でログインできない

- 環境変数 `DEFAULT_ADMIN_USERNAME` と `DEFAULT_ADMIN_PASSWORD` が正しく設定されているか確認
- データベースが正しく初期化されているかSSHで確認
- 必要に応じてデータベースファイルを削除し、アプリを再起動：
  ```bash
  rm /home/perch_database.db
  ```

### 5.3 メール送信ができない

- `EMAIL_*` 環境変数が正しく設定されているか確認
- Gmailアプリパスワードが有効か確認
- ログでSMTPエラーメッセージを確認

### 5.4 GitHub Actionsが失敗する

- GitHub Secretsがすべて設定されているか確認
- ワークフローファイルの `AZURE_WEBAPP_NAME` と `RESOURCE_GROUP` が正しいか確認
- Azure発行プロファイルが最新のものか確認

---

## 6. 更新とメンテナンス

### 6.1 コードの更新

```bash
# コードを編集
# ...

# コミットとプッシュ
git add .
git commit -m "Update feature"
git push origin main
```

プッシュすると自動的にGitHub Actionsが実行され、Azureに再デプロイされます。

### 6.2 環境変数の更新

1. GitHub Secretsを更新
2. main ブランチに空コミットをプッシュして再デプロイ：
   ```bash
   git commit --allow-empty -m "Redeploy to update environment variables"
   git push origin main
   ```

または、Azure Portalで直接環境変数を更新することもできます。

### 6.3 データベースのバックアップ

定期的にデータベースをバックアップすることをお勧めします：

```bash
# SSHでApp Serviceに接続
cp /home/perch_database.db /home/perch_database_backup_$(date +%Y%m%d).db
```

---

## 📚 参考資料

- [Flask公式ドキュメント](https://flask.palletsprojects.com/)
- [Azure App Service公式ドキュメント](https://docs.microsoft.com/ja-jp/azure/app-service/)
- [GitHub Actions公式ドキュメント](https://docs.github.com/ja/actions)
- [Gmailアプリパスワードの生成](https://myaccount.google.com/apppasswords)

---

## 🆘 サポート

問題が発生した場合は、以下を確認してください：

1. ログファイルを確認
2. 環境変数が正しく設定されているか確認
3. GitHub Actionsのワークフロー実行ログを確認
4. Azure App Serviceの診断ログを確認

それでも解決しない場合は、GitHubのIssuesで質問してください。
