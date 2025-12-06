# GitHub Secrets 自動設定スクリプト (PowerShell)
# このスクリプトはGitHub CLIを使用してSecretsを設定します

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Secrets 自動設定スクリプト" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# GitHub CLIがインストールされているか確認
Write-Host "GitHub CLI (gh) の確認中..." -ForegroundColor Yellow
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "✓ GitHub CLI が見つかりました" -ForegroundColor Green
} else {
    Write-Host "✗ GitHub CLI が見つかりません" -ForegroundColor Red
    Write-Host ""
    Write-Host "GitHub CLI をインストールしてください:" -ForegroundColor Yellow
    Write-Host "  https://cli.github.com/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "または、winget でインストール:" -ForegroundColor Yellow
    Write-Host "  winget install --id GitHub.cli" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# GitHub認証の確認
Write-Host ""
Write-Host "GitHub 認証状態の確認中..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ GitHub に認証済みです" -ForegroundColor Green
} else {
    Write-Host "✗ GitHub に認証されていません" -ForegroundColor Red
    Write-Host ""
    Write-Host "以下のコマンドで認証してください:" -ForegroundColor Yellow
    Write-Host "  gh auth login" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Secrets の設定を開始します" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$repo = "suzuki651/my-website3"

# Secretsの定義
$secrets = @{
    "SECRET_KEY" = "129fdcd8c2c21668198ca8868fe6d9371d4d5f649a03b834aa1004248e19f23d"
    "EMAIL_HOST" = "smtp.gmail.com"
    "EMAIL_PORT" = "587"
    "EMAIL_USER" = "suzuki651iris1@gmail.com"
    "EMAIL_PASSWORD" = "tkojkvjhldokssjp"
    "EMAIL_FROM" = "suzuki651iris1@gmail.com"
    "DEFAULT_ADMIN_USERNAME" = "admin"
    "DEFAULT_ADMIN_PASSWORD" = "admin1q2w3e"
    "DEFAULT_ADMIN_EMAIL" = "suzuki651iris1@gmail.com"
    "DEFAULT_ADMIN_SECURITY_QUESTION" = "あなたの最初のペットの名前は？"
    "DEFAULT_ADMIN_SECURITY_ANSWER" = "pet"
}

$count = 0
$total = $secrets.Count

foreach ($key in $secrets.Keys) {
    $count++
    Write-Host "[$count/$total] $key を設定中..." -ForegroundColor Yellow

    $value = $secrets[$key]
    echo $value | gh secret set $key --repo $repo

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $key を設定しました" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $key の設定に失敗しました" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AZURE_WEBAPP_PUBLISH_PROFILE の設定" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  注意: AZURE_WEBAPP_PUBLISH_PROFILE は手動で設定する必要があります" -ForegroundColor Yellow
Write-Host ""
Write-Host "手順:" -ForegroundColor Cyan
Write-Host "1. Azure Portal (https://portal.azure.com) にアクセス" -ForegroundColor White
Write-Host "2. hpsystem App Service を開く" -ForegroundColor White
Write-Host "3. '発行プロファイルの取得' をクリック" -ForegroundColor White
Write-Host "4. ダウンロードしたファイルの内容全体をコピー" -ForegroundColor White
Write-Host "5. 以下のコマンドを実行:" -ForegroundColor White
Write-Host ""
Write-Host "   Get-Content 'ダウンロードしたファイルのパス' | gh secret set AZURE_WEBAPP_PUBLISH_PROFILE --repo $repo" -ForegroundColor Cyan
Write-Host ""

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "設定完了の確認" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "設定されたSecretsを確認中..." -ForegroundColor Yellow
gh secret list --repo $repo

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Secrets の設定が完了しました！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Yellow
Write-Host "1. AZURE_WEBAPP_PUBLISH_PROFILE を手動で設定" -ForegroundColor White
Write-Host "2. GitHub Actions で自動デプロイが実行されます" -ForegroundColor White
Write-Host "   https://github.com/$repo/actions" -ForegroundColor Cyan
Write-Host ""
