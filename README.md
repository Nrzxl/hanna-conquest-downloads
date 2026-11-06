# HANNA conquest Mobile — Downloads

Canal público de distribuição de APKs Android da **HANNA conquest Mobile**.

Este repositório contém somente arquivos instaláveis de versões publicadas e informações públicas de atualização. **O código-fonte permanece privado** e separado deste canal.

## Situação atual

**Canal em preparação.** Ainda não existe um APK oficial publicado aqui, nem um manifesto `update.json` válido. A primeira versão será publicada após configurar a chave persistente de assinatura Android e autorizar o fluxo de distribuição.

## Instalação e atualizações

Quando o canal estiver ativo:

1. Acesse a seção **Releases** deste repositório e escolha a versão mais recente.
2. Baixe `HANNA-conquest.apk` no dispositivo Android.
3. Confira a origem e autorize a instalação no Android, se necessário.
4. As versões assinadas com a mesma chave poderão ser instaladas por cima da anterior, desde que tenham um número de build maior.
5. O aplicativo verificará o manifesto público `update.json` para informar a disponibilidade de novas versões; a instalação requer a autorização do usuário.

**Atenção:** compilações antigas de teste feitas com assinatura diferente talvez não aceitem instalação sobreposta. Não desinstale um aplicativo com dados importantes sem antes preservá-los.

## Segurança e privacidade

- Nenhuma chave de assinatura, senha, token ou código-fonte deve ser publicado neste repositório.
- O APK será publicado por um workflow do projeto privado apenas após validação e assinatura.
- Antes da primeira publicação, a inexistência de `update.json` é intencional. Não crie um manifesto apontando para um arquivo que ainda não foi publicado.
- Jogos e conquistas da prévia podem ser demonstrativos; não são dados oficiais de contas conectadas.
