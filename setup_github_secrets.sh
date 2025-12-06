#!/bin/bash

# GitHub Secrets 自動設定スクリプト (Bash)
# このスクリプトはGitHub CLIを使用してSecretsを設定します

echo "========================================"
echo "GitHub Secrets 自動設定スクリプト"
echo "========================================"
echo ""

# GitHub CLIがインストールされているか確認
echo "GitHub CLI (gh) の確認中..."
if command -v gh &> /dev/null; then
    echo "✓ GitHub CLI が見つかりました"
else
    echo "✗ GitHub CLI が見つかりません"
    echo ""
    echo "GitHub CLI をインストールしてください:"
    echo "  https://cli.github.com/"
    echo ""
    exit 1
fi

# GitHub認証の確認
echo ""
echo "GitHub 認証状態の確認中..."
if gh auth status &> /dev/null; then
    echo "✓ GitHub に認証済みです"
else
    echo "✗ GitHub に認証されていません"
    echo ""
    echo "以下のコマンドで認証してください:"
    echo "  gh auth login"
    echo ""
    exit 1
fi

echo ""
echo "========================================"
echo "Secrets の設定を開始します"
echo "========================================"
echo ""

REPO="suzuki651/my-website3"

# Secretsの設定
declare -A secrets=(
    ["SECRET_KEY"]="129fdcd8c2c21668198ca8868fe6d9371d4d5f649a03b834aa1004248e19f23d"
    ["EMAIL_HOST"]="smtp.gmail.com"
    ["EMAIL_PORT"]="587"
    ["EMAIL_USER"]="suzuki651iris1@gmail.com"
    ["EMAIL_PASSWORD"]="tkojkvjhldokssjp"
    ["EMAIL_FROM"]="suzuki651iris1@gmail.com"
    ["DEFAULT_ADMIN_USERNAME"]="admin"
    ["DEFAULT_ADMIN_PASSWORD"]="admin1q2w3e"
    ["DEFAULT_ADMIN_EMAIL"]="suzuki651iris1@gmail.com"
    ["DEFAULT_ADMIN_SECURITY_QUESTION"]="あなたの最初のペットの名前は？"
    ["DEFAULT_ADMIN_SECURITY_ANSWER"]="pet"
)

count=0
total=${#secrets[@]}

for key in "${!secrets[@]}"; do
    ((count++))
    echo "[$count/$total] $key を設定中..."

    value="${secrets[$key]}"
    echo "$value" | gh secret set "$key" --repo "$REPO"

    if [ $? -eq 0 ]; then
        echo "  ✓ $key を設定しました"
    else
        echo "  ✗ $key の設定に失敗しました"
    fi
done

echo ""
echo "========================================"
echo "AZURE_WEBAPP_PUBLISH_PROFILE の設定"
echo "========================================"
echo ""
echo "⚠️  注意: AZURE_WEBAPP_PUBLISH_PROFILE は手動で設定する必要があります"
echo ""
echo "手順:"
echo "1. Azure Portal (https://portal.azure.com) にアクセス"
echo "2. hpsystem App Service を開く"
echo "3. '発行プロファイルの取得' をクリック"
echo "4. ダウンロードしたファイルの内容全体をコピー"
echo "5. 以下のコマンドを実行:"
echo ""
echo "   cat 'ダウンロードしたファイルのパス' | gh secret set AZURE_WEBAPP_PUBLISH_PROFILE --repo $REPO"
echo ""

echo ""
echo "========================================"
echo "設定完了の確認"
echo "========================================"
echo ""
echo "設定されたSecretsを確認中..."
gh secret list --repo "$REPO"

echo ""
echo "========================================"
echo "✓ Secrets の設定が完了しました！"
echo "========================================"
echo ""
echo "次のステップ:"
echo "1. AZURE_WEBAPP_PUBLISH_PROFILE を手動で設定"
echo "2. GitHub Actions で自動デプロイが実行されます"
echo "   https://github.com/$REPO/actions"
echo ""
