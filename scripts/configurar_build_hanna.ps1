#requires -Version 5.1
<#
.SYNOPSIS
  Configura os segredos para compilar a HANNA no runner publico, sem
  tornar o codigo-fonte privado acessivel publicamente.

  Execute somente em seu proprio computador, com o keystore ORIGINAL da
  HANNA. Nunca envie chaves/senhas/tokens ao chat ou commite em Git.
#>
$ErrorActionPreference = 'Stop'
$repo = 'Nrzxl/hanna-conquest-downloads'

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw 'GitHub CLI ausente. Instale: winget install --id GitHub.cli --exact'
}

& gh auth status -h github.com *> $null
if ($LASTEXITCODE -ne 0) {
    throw 'Entre na sua conta GitHub com: gh auth login'
}

function Read-Hidden {
    param([Parameter(Mandatory=$true)][string]$Label)
    $secret = Read-Host -Prompt $Label -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
        $secret.Dispose()
    }
}

function Set-Secret {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][string]$Value
    )
    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "O segredo $Name nao pode estar vazio."
    }
    $Value | & gh secret set $Name --repo $repo
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao salvar o segredo $Name."
    }
    Write-Host "Configurado: $Name"
}

Write-Host ''
Write-Host '=== HANNA Public Build - configuracao segura ==='
Write-Host 'Somente o workflow publico e APKs sao visiveis no repositorio.'
Write-Host 'O token deve ser fine-grained e ter apenas Contents: Read'
Write-Host 'no repositorio Nrzxl/hanna-conquest-mobile (privado).'
Write-Host ''

# The user may already have finished this first step at the office.
# Never ask them to recreate a PAT when its secret name already exists.
$existing = & gh secret list --repo $repo
if ($LASTEXITCODE -ne 0) {
    throw 'Nao foi possivel conferir os segredos ja configurados.'
}
if ($existing -match '^HANNA_SOURCE_READ_TOKEN\s') {
    Write-Host 'Token de leitura ja configurado no GitHub. Preservando o segredo existente.'
} else {
    $token = Read-Hidden 'Token fine-grained de leitura do repositorio privado'
    Set-Secret -Name 'HANNA_SOURCE_READ_TOKEN' -Value $token
    $token = $null
}

Write-Host ''
Write-Host 'Selecione o .jks ORIGINAL que assinou a HANNA 0.4.3.'
Write-Host 'Nao crie outro: o Android rejeitara atualizacao por cima.'
$keystorePath = (Read-Host 'Caminho local do arquivo .jks').Trim().Trim('"')
if (-not (Test-Path -LiteralPath $keystorePath -PathType Leaf)) {
    throw 'Keystore nao encontrado. Nenhum keystore substituto foi criado.'
}
$keystoreBytes = [IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $keystorePath).Path)
if ($keystoreBytes.Length -lt 100) {
    throw 'Arquivo de keystore inesperadamente pequeno.'
}
$keystore64 = [Convert]::ToBase64String($keystoreBytes)
Set-Secret -Name 'HANNA_KEYSTORE_BASE64' -Value $keystore64
$keystoreBytes = $null
$keystore64 = $null

$alias = Read-Host 'Alias da chave original da HANNA'
Set-Secret -Name 'HANNA_KEY_ALIAS' -Value $alias
$alias = $null

$keyPassword = Read-Hidden 'Senha da chave original'
Set-Secret -Name 'HANNA_KEY_PASSWORD' -Value $keyPassword
$keyPassword = $null

$storePassword = Read-Hidden 'Senha do keystore original'
Set-Secret -Name 'HANNA_STORE_PASSWORD' -Value $storePassword
$storePassword = $null

Write-Host ''
Write-Host 'Nomes dos segredos configurados (valores nunca sao exibidos):'
& gh secret list --repo $repo
if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel conferir os segredos.' }

Write-Host ''
Write-Host 'Configuracao concluida. As etapas 1-6 foram integradas a main (0.4.9).' 
Write-Host 'Opcional: repetir validacao sem publicar APK:'
Write-Host 'gh workflow run hanna-public-apk.yml -R Nrzxl/hanna-conquest-downloads -f source_ref=main -F publish=false'
Write-Host ''
Write-Host 'Para homologar a 0.4.9 assinada SEM PUBLICAR a atualizacao automatica:'
Write-Host 'gh workflow run hanna-original-apk-validation.yml -R Nrzxl/hanna-conquest-downloads -F confirm_original=true'
Write-Host 'Baixe o artefato HANNA-0.4.9-ORIGINAL-HOMOLOGACAO na execucao do GitHub Actions.'
Write-Host 'O certificado e a versao Android serao comparados automaticamente com o APK 0.4.3.'
Write-Host 'NAO execute publish=true antes da homologacao real no telefone.'
