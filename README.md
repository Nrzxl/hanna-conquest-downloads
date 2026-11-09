# HANNA conquest Mobile — Downloads e compilação pública

Canal público de distribuição da **HANNA conquest Mobile**. O código-fonte Flutter permanece no repositório privado `Nrzxl/hanna-conquest-mobile`; não é copiado nem publicado aqui.

## Versão instalada e atualizações

O aplicativo usa [update.json](update.json) para consultar a versão, número de build, URL oficial do APK e SHA-256. Os APKs assinados ficam em [Releases](../../releases).

**Nunca desinstale a versão existente apenas para receber uma atualização.** O atualizador do Android precisa de número de build maior e da **mesma assinatura** da versão anterior. O workflow compara a assinatura com o APK atual e bloqueia publicações incompatíveis.

## Compilador público — sem consumir minutos privados

O workflow [HANNA Android — Public Build](.github/workflows/hanna-public-apk.yml) roda em runner padrão `ubuntu-latest` deste repositório **público**. Ele lê o projeto Flutter em checkout temporário, testa, compila e usa a assinatura original. Somente o APK assinado e o manifesto são publicados; não há espelho público do código-fonte.

**Primeira configuração, uma única vez:**

1. No GitHub, crie um *fine-grained Personal Access Token* com acesso somente ao repositório privado `Nrzxl/hanna-conquest-mobile`, permissão `Contents: Read-only` (metadata read é automático). Não dê escrita ou acesso a todos os repositórios.
2. Encontre seu arquivo **original** `.jks` usado na HANNA 0.4.3 e seu alias/senhas. O GitHub não permite recuperar valores dos segredos armazenados no projeto privado; não gere um novo keystore para atualizar por cima.
3. Abra **Settings → Secrets and variables → Actions** neste repositório público e cadastre os seguintes **repository secrets** (jamais como variables ou arquivos versionados):
   - `HANNA_SOURCE_READ_TOKEN`: token do passo 1
   - `HANNA_KEYSTORE_BASE64`: conteúdo Base64 **do .jks original** (sem quebras)
   - `HANNA_KEY_ALIAS`: alias original
   - `HANNA_KEY_PASSWORD`: senha da chave
   - `HANNA_STORE_PASSWORD`: senha do keystore

Alternativamente, use no Windows PowerShell 5.1 o assistente [scripts/configurar_build_hanna.ps1](scripts/configurar_build_hanna.ps1), após clonar este repositório com o GitHub CLI. Ele pede as credenciais localmente e envia diretamente como segredos do GitHub; não grava nem mostra seus valores.

```powershell
gh auth login
gh repo clone Nrzxl/hanna-conquest-downloads
cd hanna-conquest-downloads
.\scripts\configurar_build_hanna.ps1
```

**Validação da etapa 2/6 — Hall das Conquistas (sem keystore):** em **Actions → HANNA Android - Public Build → Run workflow**, escolha `source_ref = feat/mobile-0.4.5-achievement-hall` e `publish = false`. Isso executa `flutter analyze` e `flutter test` no PR #14 **sem exigir chave de assinatura, gerar APK ou alterar o aplicativo instalado**. Somente o acesso de leitura ao repositório privado precisa estar configurado.

**Publicação após o PR ser aprovado e integrado à main privada:** execute novamente com `source_ref = main` e `publish = true`, após configurar a chave original `.jks` e suas senhas. O workflow compila o APK assinado, usa número de build superior ao manifesto, compara a assinatura com o APK anterior e publica Release + `update.json`.

Também é possível disparar os dois comandos pelo GitHub CLI:

```powershell
gh workflow run hanna-public-apk.yml -R Nrzxl/hanna-conquest-downloads -f source_ref=feat/mobile-0.4.5-achievement-hall -F publish=false

# Somente após CI verde e merge do PR:
gh workflow run hanna-public-apk.yml -R Nrzxl/hanna-conquest-downloads -f source_ref=main -F publish=true
```

**Segurança:** só o proprietário `Nrzxl` pode iniciar o job com credenciais. Não há disparo por pull requests públicos nem checkout de código sugerido por terceiros. Os segredos são criptografados pelo GitHub e usados no runner; não os envie por chat, issue, commit, artifact ou log. O token de leitura pode ser revogado e recriado depois. Se um segredo antigo estiver perdido, recupere a chave original por meio do backup do proprietário antes de publicar.

## Histórico e compatibilidade

As versões anteriores continuam disponíveis em Releases. O APK deve manter o mesmo applicationId e certificado de assinatura para instalar sobre a versão anterior, e o manifesto não deve anunciar builds não verificados. A versão atual é sempre a indicada em `update.json`.
