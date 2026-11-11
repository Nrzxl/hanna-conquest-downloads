#!/usr/bin/env bash
# Configure protected GitHub Actions secrets directly from the original HANNA
# Codespace. Never uploads the private .jks to commits, releases or chat.
set -euo pipefail
set +x
umask 077

repo="Nrzxl/hanna-conquest-downloads"
keystore="/home/codespace/hanna-signing/hanna-release.jks"
expected_fingerprint="fd815741feed3fc96d92e484faa99fe423cf6116ddfc791175e2efdcaed71c5c"

if [[ ! -s "$keystore" ]]; then
  echo "ERRO: chave original nao encontrada em $keystore." >&2
  exit 1
fi
for tool in gh keytool base64; do
  command -v "$tool" >/dev/null || {
    echo "ERRO: '$tool' nao esta disponivel no Codespace." >&2
    exit 1
  }
done
gh auth status -h github.com >/dev/null || {
  echo "ERRO: autentique o GitHub CLI com 'gh auth login'." >&2
  exit 1
}

# The file was initially mode 0644. Restrict it immediately.
chmod 600 "$keystore"
echo "Chave encontrada e protegida: $keystore"
echo "Escolha o alias original mostrado pelo keytool (senha solicitada sem eco):"
keytool -list -keystore "$keystore"
read -r -p "Alias original da HANNA: " alias
if [[ -z "$alias" ]]; then
  echo "ERRO: alias vazio." >&2
  exit 1
fi

read -r -s -p "Senha do keystore original: " store_password
printf '\n'
if [[ -z "$store_password" ]]; then
  echo "ERRO: senha do keystore vazia." >&2
  exit 1
fi

# Java 17+ keytool supports -storepass:env. The secret is NOT a CLI argument
# and the printed certificate metadata contains no private key material.
if ! certificate="$(HANNA_STORE_PASSWORD="$store_password" \
    keytool -list -v -keystore "$keystore" -alias "$alias" \
    -storepass:env HANNA_STORE_PASSWORD)"; then
  echo "ERRO: nao foi possivel inspecionar o alias. Nenhum segredo enviado." >&2
  exit 1
fi
fingerprint="$(printf '%s\n' "$certificate" | awk '/SHA256:/ {print $NF; exit}' \
    | tr -d ':' | tr '[:upper:]' '[:lower:]')"
unset certificate

if [[ "$fingerprint" != "$expected_fingerprint" ]]; then
  echo "ERRO: certificado da chave nao corresponde ao APK oficial HANNA 0.4.3." >&2
  echo "Encontrado: $fingerprint" >&2
  echo "Esperado:  $expected_fingerprint" >&2
  echo "Nenhum segredo foi enviado. Nao use esta chave para atualizar o app." >&2
  exit 1
fi
echo "OK: certificado da chave original coincide exatamente com a HANNA 0.4.3."

read -r -s -p "Senha da chave privada (key password): " key_password
printf '\n'
if [[ -z "$key_password" ]]; then
  echo "ERRO: senha da chave vazia." >&2
  exit 1
fi

# Values go directly to GitHub Actions encrypted secret endpoints via STDIN.
# gh never receives the private keystore or passwords as command-line args.
printf '%s' "$alias" | gh secret set HANNA_KEY_ALIAS --repo "$repo"
base64 -w0 "$keystore" | gh secret set HANNA_KEYSTORE_BASE64 --repo "$repo"
printf '%s' "$store_password" | gh secret set HANNA_STORE_PASSWORD --repo "$repo"
printf '%s' "$key_password" | gh secret set HANNA_KEY_PASSWORD --repo "$repo"

unset store_password key_password alias fingerprint

echo "Configuracao concluida no repositorio de builds. Chave original preservada."
echo "Nao feche nem exclua o Codespace antes de fazer um BACKUP privado do arquivo .jks."
echo "Para solicitar APK 0.4.9 assinado somente para homologacao (SEM publicar OTA):"
echo "gh workflow run hanna-original-apk-validation.yml -R $repo -F confirm_original=true"
