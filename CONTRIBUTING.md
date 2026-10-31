# Contribuindo

Obrigado pelo interesse. Relate bugs com: versão do Windows, versão do Python, OBS, intervalo utilizado, horários aproximados e a mensagem de erro relevante.

**Nunca anexe** sua Web API Key, `config_local.json`, ROMs, mapper FPGA, DLLs, logs completos contendo dados privados nem gravações sem direito de redistribuição.

Para desenvolver:

1. Use Python 3 e a biblioteca padrão (sem dependências externas).
2. Rode `python -m unittest discover -s tests -v`.
3. Valide o modo `--demo` no OBS antes de testar conquistas reais.
4. Preserve a compatibilidade da URL `http://127.0.0.1:8765/overlay` e as opções existentes.
5. Não incorpore o código, o executável nem ativos do MEGA-RAW neste repositório.

Issues e propostas devem respeitar a API oficial do RetroAchievements e seus limites de uso.