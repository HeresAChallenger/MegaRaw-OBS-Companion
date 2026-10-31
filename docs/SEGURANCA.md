# Segurança e privacidade

## Chave da API

O RetroAchievements exige uma Web API Key na consulta de conquistas. O programa solicita a chave localmente com `getpass`, protege o valor com DPAPI, atrelado ao usuário Windows, e salva o resultado em:

`%LOCALAPPDATA%\MegaRawObsOverlay\config_local.json`

A API exige a chave como parâmetro de consulta `y`; ela é enviada **via HTTPS ao RetroAchievements**, mas não é fornecida à fonte Navegador do OBS. Não compartilhe arquivos de configuração nem URLs completas de requisições à API.

## Servidor local

O serviço atende somente `127.0.0.1:8765` e recusa cabeçalhos Host de outros endereços. A ação de teste utiliza POST e restringe o Origin quando presente. Isso **não** substitui as medidas de segurança de um Windows atualizado: qualquer programa rodando na mesma máquina e com acesso local poderá abrir o painel e enviar um alerta de teste.

## Publicação de conteúdo

Este repositório não deve conter:

- Web API Keys, senhas, tokens, configurações de usuário ou logs particulares.
- Gravação do som original do MEGA-RAW sem autorização para redistribuição.
- `mega_raw_gui.exe`, `mega-pro.rbf`, ROMs, arquivos de firmware, DLLs ou arquivos proprietários de terceiros.
- Emblemas copiados/baixados do RetroAchievements sem observar os direitos aplicáveis.

## Limites da API

A API impõe rate limiting. O modo 5 s é o ponto de partida sugerido; 3 s é mais frequente; 2 s é experimental. O auxiliar recua automaticamente após erros, mas isso não assegura que qualquer intervalo seja permitido sob todas as circunstâncias. Confira as [diretrizes oficiais](https://api-docs.retroachievements.org/).

## Bugs de segurança

Evite publicar segredos em Issues. Se uma chave for exposta, substitua-a no painel do RetroAchievements antes de compartilhar qualquer relatório de diagnóstico.
