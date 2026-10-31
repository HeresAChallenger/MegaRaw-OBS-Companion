# MegaRaw OBS Companion v1.4.0

Primeira versão pública organizada do auxiliar independente para exibir conquistas RetroAchievements no OBS Studio, usando um Mega Drive real com MEGA-RAW ou qualquer outro cliente compatível com a conta.

### Recursos

- Alertas transparentes com título, descrição, badge e pontos.
- Som na própria fonte Navegador.
- Teste de alertas sem login ou conquistas reais.
- Modos de 5 s (recomendado), 3 s (rápido), 10/15 s (conservadores) e 2 s (experimental).
- Armazenamento da Web API Key com DPAPI do Windows.
- Um único inicializador com menu, Python 3 sem dependências externas.

### Como usar

Extraia o ZIP, execute `INICIAR.bat`, teste a opção 1. Configure a fonte Navegador no OBS como `http://127.0.0.1:8765/overlay` (520 × 160) e ative o controle de áudio. Depois use a opção 2 durante a transmissão.

### Atenção

O pacote usa um **som demonstrativo original**, sob CC0, e não contém o áudio original do MEGA-RAW. Para utilizar outro som, substitua localmente `som_alerta.wav` por um arquivo que você tenha direito de usar.

Projeto não oficial e independente; não contém MEGA-RAW, mapper FPGA, ROMs nem arquivos de terceiros. Consulte README e segurança para detalhes.