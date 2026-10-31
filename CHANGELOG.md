# Changelog

## [1.4.0] — 2026-10-31

**Primeira organização pública do projeto independente.** Baseada no auxiliar local utilizado em testes de transmissão com Mega EverDrive PRO e MEGA-RAW Test 3.

- Overlay transparente para OBS (520 × 160), incluindo emblemas e pontuação.
- Alerta sonoro na fonte Navegador com WAV substituível.
- Painel e notificação de demonstração.
- Modos de consulta RetroAchievements em 2, 3, 5, 10 e 15 segundos.
- Consulta local da fonte a cada 250 ms.
- Web API Key protegida pelo Windows DPAPI; servidor vinculado ao localhost.
- Proteção adicional para validar o cabeçalho Host local e limitar consultas sobrepostas.
- Um único `INICIAR.bat` com menu de modos.
- Documentação PT-BR/EN, testes básicos e fluxo de publicação GitHub.
- **Arquivo de áudio pessoal removido do pacote público**, substituído por som CC0 original.

### Limitações conhecidas

- Não possui acesso ao evento interno do MEGA-RAW; depende da API oficial.
- O intervalo de 2 s pode sofrer limitação de requisições (HTTP 429).
- O navegador do OBS pode exigir atualização de cache depois da reinicialização.