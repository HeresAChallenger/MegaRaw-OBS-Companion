# MegaRaw OBS Companion

**Notificações de achievements do RetroAchievements no OBS Studio, para quem joga no Mega Drive real com MEGA-RAW.**

[English version](README.en.md) · [Histórico de versões](CHANGELOG.md) · [Segurança](docs/SEGURANCA.md)

> Projeto **independente e não oficial**, mantido por [@HeresAChallenger](https://github.com/HeresAChallenger). Não é parte do MEGA-RAW, do RetroAchievements, do OBS Studio ou da Krikzz. O MEGA-RAW original é desenvolvido por [Liqui](https://github.com/liquid-wq/mega-raw) e possui licença própria. Este repositório **não inclui** o programa, firmware, mapper FPGA, bibliotecas ou ROMs do MEGA-RAW.

## O que faz

- Detecta **conquistas confirmadas** pela [API pública do RetroAchievements](https://api-docs.retroachievements.org/v1/get-user-recent-achievements.html).
- Exibe no OBS um alerta transparente com **nome, descrição, emblema, jogo e pontos**.
- Toca um efeito sonoro na própria fonte Navegador do OBS.
- Fornece **painel local** e botão de **notificação de demonstração**, sem gastar uma conquista.
- Oferece modos de consulta de **2, 3, 5, 10 ou 15 segundos** (2 s experimental).
- Mantém a **Web API Key protegida pelo Windows (DPAPI)**, fora da pasta do aplicativo.
- Usa **Python 3 e somente a biblioteca padrão**; não altera o MEGA-RAW, o EverDrive PRO nem as ROMs.

**Nota de latência:** a notificação aparece depois que a API registra a conquista, não necessariamente no instante em que o MEGA-RAW mostra seu próprio pop-up. O modo de 3 s é mais rápido, mas também gera mais chamadas. A API possui limite de requisições; recomenda-se começar com 5 s.

## Requisitos

- Windows 10/11, Python 3 instalado e acessível pelo comando `python` ou `py -3`.
- OBS Studio com fonte **Navegador**.
- Conta RetroAchievements e **Web API Key** (somente para uso real; a demonstração não precisa).
- Opcional: MEGA-RAW no console original. **Não há comunicação direta** entre este auxiliar e o executável do MEGA-RAW; ele monitora a conta no RetroAchievements. Pode exibir conquistas de qualquer cliente Mega Drive associado à conta.

## Primeira execução (Windows)

1. Baixe o ZIP da [release](https://github.com/HeresAChallenger/MegaRaw-OBS-Companion/releases) ou o conteúdo deste repositório.
2. Extraia todos os arquivos para uma pasta, por exemplo `C:\MegaRaw-OBS-Companion`.
3. Execute **`INICIAR.bat`** e escolha **1 — Demonstração**.
4. No OBS, adicione **Fontes → + → Navegador**:

   | Propriedade | Valor |
   | --- | --- |
   | URL | `http://127.0.0.1:8765/overlay` |
   | Largura | `520` |
   | Altura | `160` |
   | Controlar áudio via OBS | Ativado |
   | Visibilidade | Ativa; fonte acima da captura do console |

5. No navegador, abra `http://127.0.0.1:8765/painel` e clique em **Exibir notificação de teste**. Verifique imagem e medidor de áudio no OBS.
6. Volte ao menu (encerre a execução com `Ctrl+C` na janela do auxiliar) e escolha **2 — LIVE 5 segundos**. Informe usuário e chave do RetroAchievements na primeira execução. Aguarde **Monitorando conquistas** antes de desbloquear achievements.

**O programa deve permanecer aberto durante a transmissão.** O OBS não inicia o servidor por conta própria. Após reiniciar o PC, execute `INICIAR.bat` novamente.

### Se o alerta sumir depois de reiniciar

Abra a fonte Navegador no OBS e use **Atualizar cache da página atual**. Confira se `http://127.0.0.1:8765/painel` abre no navegador e se a janela do auxiliar continua aberta. O cache da fonte pode sobreviver à interrupção do servidor local.

### Som do alerta

O ZIP público acompanha um **som demonstrativo original e livre (CC0)**, **não** uma gravação do som original do MEGA-RAW. Para usar um som próprio, substitua `som_alerta.wav` por um WAV que você tenha direito de usar; reinicie o auxiliar e atualize o cache da fonte no OBS.

Se o OBS não transmitir o áudio, marque **Controlar áudio via OBS**, confira o canal da fonte no mixer e ajuste **Propriedades avançadas de áudio → Monitorar e enviar para a saída** apenas se também quiser escutá-lo nos fones. Se capturar áudio do Windows e da fonte ao mesmo tempo, poderá ouvir duplicações.

## Executar sem arquivo BAT

```powershell
python mega_raw_obs.py --demo
python mega_raw_obs.py --interval 5
python mega_raw_obs.py --interval 3
python mega_raw_obs.py --interval 2  # experimental; pode gerar HTTP 429
python mega_raw_obs.py --reset       # remove configuração local desta aplicação
```

## Segurança e privacidade

A chave é solicitada localmente e armazenada, criptografada por DPAPI, em `%LOCALAPPDATA%\MegaRawObsOverlay\config_local.json`. Ela **não deve entrar no GitHub** e não é enviada ao navegador do OBS. O servidor local escuta apenas `127.0.0.1:8765`.

Não envie ao GitHub o arquivo de configuração, logs de uso, gravações particulares ou a gravação do som original sem verificar seus direitos de distribuição. Leia [SEGURANCA.md](docs/SEGURANCA.md).

## Limitações

- Funciona por **polling** da API, portanto pode haver atraso de rede e do serviço.
- O programa ignora as conquistas que já estavam na lista quando o monitor inicia.
- Apenas conquistas com `ConsoleName` de Mega Drive/Genesis são exibidas, por padrão.
- O pop-up exibido no OBS **não é uma captura pixel-a-pixel** da janela temporária do MEGA-RAW.
- Sem suporte a Linux/macOS na autenticação persistente: ela utiliza o DPAPI do Windows.
- Para evitar excessos de chamadas, reduza a frequência quando houver erro HTTP 429.

## Desenvolvimento

```bash
python -m unittest discover -s tests -v
```

Consulte [ARQUITETURA.md](docs/ARQUITETURA.md), [CONTRIBUTING.md](CONTRIBUTING.md) e [PUBLICACAO.md](docs/PUBLICACAO.md).

## Créditos e licenciamento

- **MegaRaw OBS Companion** — projeto independente de [@HeresAChallenger](https://github.com/HeresAChallenger), código MIT (veja [LICENSE](LICENSE)).
- **MEGA-RAW** — projeto separado de [Liqui](https://github.com/liquid-wq/mega-raw), sujeito à sua própria licença. **Nenhum arquivo dele é redistribuído aqui.**
- **RetroAchievements** — dados e emblemas pertencem ao serviço e seus colaboradores; marca independente.
- **OBS Studio** — usado apenas como aplicação compatível.
- **Som de demonstração** — sintetizado especificamente para este projeto e dedicado sob CC0, veja [AUDIO-LICENSE.txt](AUDIO-LICENSE.txt).