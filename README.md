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
Set-Location $env:USERPROFILE
# Execute gh auth login apenas se ainda não estiver autenticado.
gh repo clone Nrzxl/hanna-conquest-downloads
Set-Location .\hanna-conquest-downloads
.\scripts\configurar_build_hanna.ps1
```

**Validação das etapas 1–5/6 — Rota do 100%, Hall, Início inteligente, Loja Steam/retro e Coleção Retro Premium:** os PRs #13–#17 foram integrados à `main` privada, com validações públicas aprovadas. O código está na versão **0.4.8**; o APK público permanece na **0.4.3** enquanto não for recuperado o `.jks` original. Para repetir a análise e os testes sem assinatura, escolha `source_ref = main` e `publish = false`. Esse modo **não gera APK**. A wishlist funciona quando o acesso público é permitido pela Steam e a classificação de promoções considera só preços BRL realmente verificados; a vitrine retro salva objetivos, sem registrar compras ou conceder conquistas.

**Publicação após o PR ser aprovado e integrado à main privada:** execute novamente com `source_ref = main` e `publish = true`, após configurar a chave original `.jks` e suas senhas. O workflow compila o APK assinado, usa número de build superior ao manifesto, compara a assinatura com o APK anterior e publica Release + `update.json`.

Também é possível disparar os dois comandos pelo GitHub CLI:

```powershell
gh workflow run hanna-public-apk.yml -R Nrzxl/hanna-conquest-downloads -f source_ref=main -F publish=false

# Somente após a recuperacao do .jks original, com a main testada:
gh workflow run hanna-public-apk.yml -R Nrzxl/hanna-conquest-downloads -f source_ref=main -F publish=true
```

**Segurança:** só o proprietário `Nrzxl` pode iniciar o job com credenciais. Não há disparo por pull requests públicos nem checkout de código sugerido por terceiros. Os segredos são criptografados pelo GitHub e usados no runner; não os envie por chat, issue, commit, artifact ou log. O token de leitura pode ser revogado e recriado depois. Se um segredo antigo estiver perdido, recupere a chave original por meio do backup do proprietário antes de publicar.

## Histórico e compatibilidade

As versões anteriores continuam disponíveis em Releases. O APK deve manter o mesmo applicationId e certificado de assinatura para instalar sobre a versão anterior, e o manifesto não deve anunciar builds não verificados. A versão atual é sempre a indicada em `update.json`.
