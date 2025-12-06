# Azure Service Principal 設定ガイド

## 🔐 なぜService Principalが必要か？

Azureで**基本認証が無効**になっているため、従来の発行プロファイル（Publish Profile）を使ったデプロイができません。
代わりに、**Service Principal（サービスプリンシパル）**を使用した認証方式に切り替える必要があります。

## 📋 設定手順

### ステップ1: サブスクリプションIDの確認

1. Azure Portal (https://portal.azure.com) にアクセス
2. 上部の検索バーで「サブスクリプション」を検索
3. 使用しているサブスクリプションをクリック
4. **サブスクリプションID**をコピー（以下の手順で使用します）

例: `12345678-1234-1234-1234-123456789abc`

### ステップ2: Cloud Shellを開く

1. Azure Portal の右上にあるCloud Shellアイコン（`>_`）をクリック
2. BashまたはPowerShellを選択（Bashを推奨）
3. ストレージが必要な場合は作成

### ステップ3: Service Principalの作成

Cloud Shellで以下のコマンドを実行します。
**{subscription-id}** の部分は、ステップ1でコピーしたサブスクリプションIDに置き換えてください。

```bash
az ad sp create-for-rbac --name "github-actions-hpsystem" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/ccc/providers/Microsoft.Web/sites/hpsystem \
  --sdk-auth
```

#### 実際の例:
サブスクリプションIDが `12345678-1234-1234-1234-123456789abc` の場合:

```bash
az ad sp create-for-rbac --name "github-actions-hpsystem" \
  --role contributor \
  --scopes /subscriptions/12345678-1234-1234-1234-123456789abc/resourceGroups/ccc/providers/Microsoft.Web/sites/hpsystem \
  --sdk-auth
```

### ステップ4: 出力されたJSONをコピー

コマンドを実行すると、以下のようなJSON形式の出力が表示されます：

```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "12345678-1234-1234-1234-123456789abc",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

**⚠️ 重要**: このJSON全体をコピーしてください。特に `clientSecret` は二度と表示されません！

### ステップ5: GitHub Secretsに追加

1. GitHub リポジトリ (https://github.com/suzuki651/my-website3) を開く
2. **Settings** → **Secrets and variables** → **Actions** に移動
3. **New repository secret** をクリック
4. 以下の情報を入力:
   - **Name**: `AZURE_CREDENTIALS`
   - **Value**: ステップ4でコピーしたJSON全体
5. **Add secret** をクリック

## ✅ 確認

GitHub Secretsページで、`AZURE_CREDENTIALS` が追加されていることを確認してください。

## 🔄 その他の必要なシークレット

`AZURE_CREDENTIALS` の他に、以下のシークレットも設定する必要があります：

1. SECRET_KEY
2. EMAIL_HOST
3. EMAIL_PORT
4. EMAIL_USER
5. EMAIL_PASSWORD
6. EMAIL_FROM
7. DEFAULT_ADMIN_USERNAME
8. DEFAULT_ADMIN_PASSWORD
9. DEFAULT_ADMIN_EMAIL
10. DEFAULT_ADMIN_SECURITY_QUESTION
11. DEFAULT_ADMIN_SECURITY_ANSWER

詳細は `GITHUB_SECRETS_SETUP.md` を参照してください。

## 🚀 デプロイ

すべてのシークレットを設定したら：

1. GitHub の **Actions** タブを確認
2. ワークフローが自動実行されます
3. すべてのステップが緑色になれば成功！

## ❓ トラブルシューティング

### エラー: "Insufficient privileges to complete the operation"

**原因**: サブスクリプションに対する権限が不足しています。

**解決方法**:
1. Azure Portal で自分のロール（役割）を確認
2. 最低でも「共同作成者」または「所有者」ロールが必要
3. 権限がない場合は、管理者に依頼してください

### エラー: "Resource not found"

**原因**: リソースグループ名またはApp Service名が間違っています。

**解決方法**:
1. Azure Portal で正しいリソースグループ名を確認（現在: `ccc`）
2. App Service名を確認（現在: `hpsystem`）
3. コマンドのパスを修正して再実行

### エラー: "--sdk-auth is deprecated"

**原因**: `--sdk-auth` オプションは非推奨ですが、現在のワークフローではまだ必要です。

**解決方法**: 警告は無視して、出力されたJSONを使用してください。

## 📚 参考資料

- [Azure Service Principal について](https://docs.microsoft.com/ja-jp/azure/active-directory/develop/app-objects-and-service-principals)
- [GitHub Actions での Azure 認証](https://docs.microsoft.com/ja-jp/azure/developer/github/connect-from-azure)
- [Azure CLI リファレンス](https://docs.microsoft.com/ja-jp/cli/azure/ad/sp)

---

**設定完了日**: _________________

**作成したService Principal名**: github-actions-hpsystem
