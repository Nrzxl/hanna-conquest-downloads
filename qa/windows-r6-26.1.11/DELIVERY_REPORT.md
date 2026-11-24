# HANNA conquest Windows R6 26.1.11 — entrega oficial

## Publicação do programa: PASS

[Release oficial](https://github.com/Nrzxl/hanna-conquest-downloads/releases/tag/v26.1.11) · [Instalador x64](https://github.com/Nrzxl/hanna-conquest-downloads/releases/download/v26.1.11/HANNA_conquest_Setup_R6_26_1_11_x64.exe) · [SHA-256 dos arquivos](https://github.com/Nrzxl/hanna-conquest-downloads/releases/download/v26.1.11/SHA256SUMS.txt).

Setup: **59.627.520 bytes**, SHA-256 `d514747c8b2cebb61e6cb07148fdc48912b7bc74a63805fd0b6200d20ca06f1e`. Download público anônimo confirmado. EXE correto 26.1.11.0, programa completo com Python/Tcl/Tk e identidade do aplicativo existente. NotSigned: sem certificado Authenticode.

Código distribuído: `b1f1a9d1de7d814729b16a61eb43f3149ed67fd1`; identidade de conteúdo `856d74051d820caa526753933d61a763b5c6a8e25af5fe81a8762c9c89fcbbcd`. PR #36 permanece draft, sem merge.

CI oficial [45307569591](https://github.com/Nrzxl/hanna-conquest-downloads/actions/runs/45307569591) aprovado. Publicação [45380708667](https://github.com/Nrzxl/hanna-conquest-downloads/actions/runs/45380708667) aprovada. O primeiro job de publicação falhou ao consultar a tag do rascunho: o rascunho 456641626 e seus cinco arquivos foram preservados, conferidos por hashes e retomados pelo ID, sem nova Release ou reenvio.

## Integridade e QA

| Verificação | Resultado |
|---|---|
| Testes afetados locais | 58 PASS / 0 FAIL / 0 SKIP |
| Mesmos testes no CI oficial | 58 PASS / 0 FAIL / 0 SKIP; não somar como 116 testes distintos |
| Controles do pacote oficial efetivamente baixado | 14 PASS / 0 FAIL |
| Jornada no EXE oficial | 21/21 PASS; 21 hashes de capturas; zero callbacks |
| Controle de recuperação em viewports nativos | 3/3 PASS |
| Atualização, reaplicação e falha injetada | PASS em perfil sintético isolado |
| Rollback 26.1.11 e 26.1.9, Registro e desinstalação QA | PASS; perfil preservado |
| ZIP completo | 62.612.707 bytes; CRC e 62 hashes PASS |
| Conteúdo incorporado ao Setup | CRC e 6.660 hashes PASS; 2.085 arquivos de runtime |
| Sanitização do payload | 1.327 textos verificados; zero credenciais encontradas; zero arquivos de dados pessoais |
| Download público do Setup e ZIP pelo atualizador | PASS, sem token e sem instalar |
| Atualizador quando já está na 26.1.11 | PASS: não oferece a mesma versão como nova |

ZIP completo SHA-256: `e036561f71905076dfe9c4d3a09f6ade1ff1a982eb4c4d6bc6898f996eb1fc84`.
Cumulativo SHA-256: `39405b76aefd466595ed81958bb56bf81ebbbfae8353241cebae86829a0cd15e`.

Os ajustes de retomada foram somente no roteiro QA (pasta isolada e variáveis); o código distribuído permaneceu idêntico ao CI. Etapas já aprovadas de instalação não foram repetidas. Regressão histórica 1.050 PASS e Diagnóstico Mestre 304 PASS preservados, não reexecutados nesta marcação. A falha gráfica histórica do runner permanece identificada como FAIL histórico; nove casos afetados passaram localmente sem relaxar critérios.

## Instalação neste computador: BLOCKED

O programa pode ser distribuído com seus gates de integridade e recuperação aprovados; isso não autoriza nem executa a instalação pessoal. C: ainda não comporta a transação mantendo a reserva exigida. As margens não foram diminuídas. O instalador reavalia o espaço e recusa a atualização antes de alterar o perfil ou substituir arquivos se a reserva não for atendida.

Os três temporários autorizados foram transferidos para D: com hashes, recuperando 252.112.896 bytes. Sete cópias antigas de programa QA (770.996.750 bytes), incluindo cinco cópias de recuperação, foram integralmente copiadas e verificadas em D:. Continuam também em C:. A retirada adicional e os dois registros dos aplicativos QA foram bloqueados pela revisão automática por falta de autorização específica. A pergunta está pendente; nenhuma exclusão adicional foi executada. Perfis, backups de dados, pacotes finais e instalação pessoal intactos.

PASS em D: para backup integral, preservando a reserva de 8.589.934.592 bytes. C: exige a reserva intacta de 7.651.259.719 bytes mais 490.847.854 bytes para a transação. Consulte OFFICIAL_STORAGE_READY.json para a medição, que o instalador repetirá antes da aplicação.

## Como atualizar quando o espaço estiver liberado

1. Salvar o instalador em D: e fechar a HANNA.
2. Executar o Setup oficial, manter D:\HANNA como destino do backup e selecionar **Fazer backup e atualizar**. Não desinstalar a versão atual.
3. Abrir pelo mesmo atalho, conferir 26.1.11 e executar Ctrl+Shift+D para homologação pessoal.

A primeira transição usa o Setup. A 26.1.9 ainda usa o transporte privado antigo e não extrai o novo root_payload: não declarar que a interface antiga encontra/aplica esta Release pública. As próximas versões usam Configurações → Atualizações da 26.1.11, cujo transporte público já foi testado contra a Release real, sem token. Nenhum segundo aplicativo permanente é criado.

## Gates pessoais separados

Instalação pessoal, Ctrl+Shift+D físico, importação e ativação pessoal: NOT_RUN. Dois vínculos antigos e três jogos sem ID nativo confirmado continuam protegidos. Não vincular por título. Somente collection/collectionItem compartilhados; quatro modelos permanecem locais. A confirmação Android principal 0.4.18 e a leitura Windows da revisão 56 continuam preservadas, com o nome literal realmente recebido, sem novas operações.

Perfil, configurações, contas, biblioteca, artes, cases e backups preservados. Sem alteração de backend, SQL, Flutter, OTA Android, merge ou R7. **deployment_verified=false; personal_sync_activation_allowed=false.**
