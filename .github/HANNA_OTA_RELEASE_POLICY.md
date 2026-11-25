# HANNA conquest Mobile — política oficial de atualizações Android

**Regra permanente aprovada pelo usuário em 13/11/2026:** o APK **válido** deve chegar ao Android pelo **atualizador interno HANNA**, sem exigir instalação manual do arquivo ou autorização adicional de homologação para cada build. O botão de atualização é o fluxo principal; o link do APK é apenas contingência.

## Regra confirmada novamente em 25/11/2026 — publicação direta por padrão

O usuário reiterou que **toda atualização aprovada tecnicamente precisa aparecer no atualizador interno HANNA**, inclusive as versões com correções de tradução e interface. Isto é uma **autorização permanente de publicação automática após CI**, não uma autorização para ignorar CI, certificado, segurança, hashes ou compatibilidade.

- Não exigir novo teste físico manual ou aprovação por build como pré-condição geral. QA físico continua útil como diagnóstico posterior e como bloqueio **somente** quando houver migração destrutiva, credenciais, instalação incompatível ou escrita pessoal explicitamente protegida.
- O workflow **main** de cada release precisa encadear, sem intervenção humana, `flutter analyze`, `flutter test`, APK com keystore original e SHA, teste **in-place** nos Android 10/API29 e 15/API35, Release GitHub oficial com APK+sidecar, validador independente de `hanna_ota_promote_verified.py` e publicação monotônica em `main/update.json`.
- A versão anterior permanece disponível até que **todos** os passos sejam PASS. Falha em qualquer etapa **não** vira um link manual do APK como solução principal. Diagnosticar/corrigir CI e reexecutar a publicação.
- O job de promoção deve usar o script verificador existente como fonte de verdade. Quando o GitHub não agendar o job com `uses: ./.github/workflows/hanna-ota-promote-verified.yml` (incidente comprovado na 0.4.19, run #45473038586), preferir job comum `runs-on: ubuntu-latest`, `needs: signed-validation`, `permissions: contents: write, actions: read`, Android SDK, **exatamente o mesmo script**, commit somente de `update.json`, sem pular validações.
- Uma compilação de QA em branch separada não publica OTA. Criar/promover um workflow de produção sobre `main` com fonte imutável, assinatura original e todos os gates. O usuário só precisa tocar no ícone **Atualizar** da HANNA; o Android não é instalado silenciosamente.
- Mantêm-se protegidos `deployment_verified=false`, importação de dados pessoais e qualquer alteração no Windows R6. O publishable key pública não habilita automaticamente o Sync pessoal.

Exemplo real deste padrão: `.github/workflows/hanna-0420-android-official-ota.yml`. O primeiro job assina/testa/publica o Release **após ambos os testes de emulador**; o segundo job normal usa `hanna_ota_promote_verified.py` e só então publica `update.json`.

## Obrigatório em todas as novas versões

1. Código Flutter e testes aprovados (`flutter analyze` e `flutter test`).
2. APK Android *release* com **certificado original**, `applicationId` imutável e `versionCode` estritamente crescente.
3. SHA-256 verificado e release oficial GitHub com APK + sidecar `.sha256`; verificar APK anterior e novo por `apksigner` e `aapt`.
4. Acionar **depois do job assinado** o verificador oficial `.github/scripts/hanna_ota_promote_verified.py` (pelo workflow reutilizável quando agendado corretamente, ou por um segundo job normal com `needs` e as mesmas verificações) para publicar `update.json` no `main`. A publicação é monotônica, serializada, idempotente e bloqueia APK incompatível, falha de teste, mesmo build com SHA diferente ou rollback.
5. Conferir `https://raw.githubusercontent.com/Nrzxl/hanna-conquest-downloads/main/update.json?hanna_refresh=BUILD` e indicar ao usuário **Atualizar pelo ícone da HANNA**. Não pedir para baixar APK manualmente como caminho principal.
6. Em caso de falha de validação, **não publicar OTA**; conservar a versão anterior e reportar o erro e a execução do GitHub.
7. Não alterar Windows R6/R7, não remover dados de usuário, não distribuir keystores ou segredos no repositório público.
8. Quando mudanças envolvem tradução, rede, biblioteca ou sincronização, manter logs diagnósticos sem credenciais e tratar falhas com fallback ao estado anterior.

## Integração para todo novo workflow assinado (reutilizável ou job normal validado)

Após o job `signed-validation` (que deve usar o nome **Build and prove in-place upgrade compatibility** e conter os gates do `hanna-0414-android-preview.yml`), adicionar um job:

```yaml
  publish-ota:
    needs: signed-validation
    if: ${{ needs.signed-validation.result == 'success' }}
    permissions:
      contents: write
      actions: read
    uses: ./.github/workflows/hanna-ota-promote-verified.yml
    with:
      release_tag: v0.4.15-b10358-preview # substituir pelo tag verificado
      source_run_id: ${{ github.run_id }}
      release_notes: "HANNA 0.4.15: descrição objetiva das novidades."
```

Se o workflow de build usar um nome ou sequência de verificações diferente, atualizar conjuntamente os validadores em `.github/scripts/hanna_ota_promote_verified.py` e seus testes antes de tentar promover qualquer APK. **Nunca retirar os gates para forçar uma publicação.**

O workflow reutilizável também possui `workflow_dispatch` para recuperação manual em situações excepcionais, mediante indicação do tag e run original validado. Não depende de acordar o PC ou da presença do usuário no GitHub.

## Estado em 13/11/2026

- **0.4.14 / 10357**: assinado, aprovado e publicado no atualizador `update.json`.
- Repositório de código: `Nrzxl/hanna-conquest-mobile`.
- Distribuição/OTA: `Nrzxl/hanna-conquest-downloads`.
- O Android ainda decide quando consultar a nuvem (início/ícone); **publicar OTA não instala nada silenciosamente** no dispositivo.
