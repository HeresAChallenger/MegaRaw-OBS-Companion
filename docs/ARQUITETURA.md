# Arquitetura

```
Mega Drive / MEGA-RAW (aplicativo separado)
         │ desbloqueio confirmado no site
         ▼
API RetroAchievements (HTTPS, API_GetUserRecentAchievements)
         │ consulta periódica: 2, 3, 5, 10 ou 15 s
         ▼
mega_raw_obs.py (Windows, Python 3, biblioteca padrão)
         │ fila de eventos em memória; servidor 127.0.0.1:8765
         ▼
OBS Browser Source: /overlay (HTTP local)
         │ checagem a cada 250 ms
         ▼
Notificação transparente + áudio WAV
```

## Endpoints locais

| Caminho | Uso |
| --- | --- |
| `/painel` | status e botão de demonstração |
| `/overlay` | HTML/JS transparente para OBS |
| `/audio/alert.wav` | arquivo de áudio local |
| `/api/status` | status da conexão e último evento |
| `/api/events?after=N` | eventos novos na memória |
| `/api/test` (POST) | injeta evento demonstrativo |

O primeiro polling apenas constrói a lista de conquistas já existentes. Desbloqueios posteriores são acrescentados à fila. A fonte Navegador consulta os eventos locais a cada 250 ms. O HTML é embutido no Python; não há dependências web externas para funcionamento do painel (as imagens de badges vêm do RetroAchievements).

## Limitações de design

- **Não lê o `trigger_log.txt`** do MEGA-RAW, pois esse arquivo pode não ser produzido em certas instalações.
- **Não intercepta nem captura** o popup original do MEGA-RAW.
- Um alerta só é emitido após aparecer entre os desbloqueios retornados pela API.
- O aplicativo não grava uma fila persistente de eventos; ao reiniciar, não repete conquistas antigas.
- A API pode reportar desbloqueios de outro cliente Mega Drive associado à mesma conta; não há prova de que vieram do EverDrive PRO.
- O servidor fica ligado enquanto o processo Python estiver aberto; o OBS não o inicializa.

## Licenciamento

Código e documentação próprios: MIT. Som de demonstração próprio: CC0. Nenhum componente do MEGA-RAW é distribuído. Caso se deseje integração direta via evento interno, é necessário um mecanismo suportado pelo autor do MEGA-RAW ou autorização/licenciamento compatível.