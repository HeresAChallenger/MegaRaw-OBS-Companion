# MegaRaw OBS Companion

An **unofficial**, independent Windows/Python 3 companion that shows confirmed RetroAchievements unlocks in an OBS Studio transparent Browser Source. Designed for people who use MEGA-RAW on an original Sega Mega Drive / Genesis, but it does **not** connect directly to or modify MEGA-RAW.

**[Leia em português](README.md)**

## Features

- Monitors confirmed achievements through the [RetroAchievements recent unlocks API](https://api-docs.retroachievements.org/v1/get-user-recent-achievements.html).
- Displays title, description, badge, game and points in the OBS Browser Source.
- Optional WAV alert played directly by the Browser Source.
- Built-in localhost dashboard and harmless demo alert.
- Configurable 2/3/5/10/15-second polling intervals; 2 seconds is experimental and can hit API rate limits.
- Uses Windows DPAPI to encrypt your API key locally; no third-party Python packages.

## Quick start

1. Extract the release on Windows 10/11 with Python 3 installed.
2. Run `INICIAR.bat`, choose `1` (demo) first.
3. Add a Browser Source in OBS: `http://127.0.0.1:8765/overlay`, size **520 x 160**; enable **Control audio via OBS**.
4. Open `http://127.0.0.1:8765/painel`, test the alert.
5. Re-run using menu option `2` (5-second live mode), and supply your RetroAchievements username and **Web API Key**.
6. Leave the program open while broadcasting; start it again after reboot.

For Windows Browser Source cache problems, refresh the source's current page after the server is running.

## Privacy and rights

Your API key is stored under `%LOCALAPPDATA%\MegaRawObsOverlay\config_local.json`, encrypted for the current Windows user using DPAPI. Never commit credentials, logs or user recordings. The bundled `som_alerta.wav` is an **original, CC0 demo sound**, not MEGA-RAW's actual sound. Replace it locally only with audio you have permission to use.

This companion is MIT licensed; it does not include any MEGA-RAW executable, `.rbf`, Qt libraries, private recordings or ROMs. MEGA-RAW is an independent project by [Liqui](https://github.com/liquid-wq/mega-raw) and has its own license. RetroAchievements and OBS Studio are separate services/products. There is no endorsement or affiliation.

For details, see [README.md](README.md), [architecture](docs/ARQUITETURA.md) and [security](docs/SEGURANCA.md).