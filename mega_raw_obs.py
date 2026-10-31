#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unofficial companion for RetroAchievements overlays in OBS.
Runs independently of MEGA-RAW. Uses only Python 3 standard library.
"""
from __future__ import annotations

import argparse
import base64
import ctypes
import getpass
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from collections import deque
from ctypes import wintypes
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_HOME = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'MegaRawObsOverlay'
CONFIG_PATH = DATA_HOME / 'config_local.json'
LOG_PATH = DATA_HOME / 'integracao.log'
PORT = 8765
SOUND_PATH = HERE / 'som_alerta.wav'  # generic sound distributed under CC0; replace locally if desired
INTERVAL = 10  # seconds between API checks; experimental 2/3 seconds are optional
RA_ENDPOINT = 'https://retroachievements.org/API/API_GetUserRecentAchievements.php'
RA_ORIGIN = 'https://retroachievements.org'
LOCK = threading.RLock()


class State:
    def __init__(self):
        self.events = deque(maxlen=100)
        self.seq = 0
        self.error = ''
        self.mode = 'Inicializando'
        self.username = ''
        self.last_check = ''
        self.last_unlock = ''
        self.online = False
        self.demo = False
        self.only_megadrive = True
        self.interval = INTERVAL

    def add_event(self, event):
        with LOCK:
            self.seq += 1
            ev = {'seq': self.seq, **event}
            self.events.append(ev)
            self.last_unlock = event['title']
            return ev


STATE = State()


def log(message):
    stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{stamp}] {message}'
    print(line, flush=True)
    try:
        DATA_HOME.mkdir(parents=True, exist_ok=True)
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > 800_000:
            LOG_PATH.replace(DATA_HOME / 'integracao_antigo.log')
        with LOG_PATH.open('a', encoding='utf-8') as f:
            f.write(line + '\n')
    except OSError:
        pass


def _protect(secret):
    """Protect the API key with user-scoped Windows DPAPI."""
    if sys.platform != 'win32':
        raise RuntimeError('Proteção DPAPI disponível somente no Windows.')

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_ubyte))]

    raw = secret.encode('utf-8')
    holder = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
    src = DATA_BLOB(len(raw), ctypes.cast(holder, ctypes.POINTER(ctypes.c_ubyte)))
    dest = DATA_BLOB()
    crypto = ctypes.WinDLL('Crypt32', use_last_error=True)
    kernel = ctypes.WinDLL('Kernel32', use_last_error=True)
    crypto.CryptProtectData.argtypes = [ctypes.POINTER(DATA_BLOB), wintypes.LPCWSTR, ctypes.c_void_p,
                                        ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
    crypto.CryptProtectData.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    # CRYPTPROTECT_UI_FORBIDDEN = 0x1
    if not crypto.CryptProtectData(ctypes.byref(src), 'MEGA RAW OBS API', None, None, None, 1, ctypes.byref(dest)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return base64.b64encode(ctypes.string_at(dest.pbData, dest.cbData)).decode('ascii')
    finally:
        kernel.LocalFree(ctypes.cast(dest.pbData, ctypes.c_void_p))


def _unprotect(data):
    if sys.platform != 'win32':
        raise RuntimeError('Proteção DPAPI disponível somente no Windows.')

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_ubyte))]

    raw = base64.b64decode(data)
    holder = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
    src = DATA_BLOB(len(raw), ctypes.cast(holder, ctypes.POINTER(ctypes.c_ubyte)))
    dest = DATA_BLOB()
    crypto = ctypes.WinDLL('Crypt32', use_last_error=True)
    kernel = ctypes.WinDLL('Kernel32', use_last_error=True)
    crypto.CryptUnprotectData.argtypes = [ctypes.POINTER(DATA_BLOB), ctypes.c_void_p, ctypes.c_void_p,
                                          ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
    crypto.CryptUnprotectData.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if not crypto.CryptUnprotectData(ctypes.byref(src), None, None, None, None, 1, ctypes.byref(dest)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(dest.pbData, dest.cbData).decode('utf-8')
    finally:
        kernel.LocalFree(ctypes.cast(dest.pbData, ctypes.c_void_p))


def config():
    if CONFIG_PATH.exists():
        obj = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
        return obj['usuario'], _unprotect(obj['chave_api_protegida']), bool(obj.get('somente_megadrive', True))
    print('\nCONFIGURAÇÃO INICIAL — MEGA-RAW + OBS')
    print('Obtenha sua Web API Key em https://retroachievements.org/controlpanel.php (Keys).')
    print('A chave será criptografada pelo Windows para seu usuário; não é transmitida ao OBS.\n')
    user = input('Usuário do RetroAchievements: ').strip()
    key = getpass.getpass('Web API Key (não aparece na tela): ').strip()
    if not user or not key:
        raise ValueError('Usuário e chave são obrigatórios.')
    secured = _protect(key)
    DATA_HOME.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps({'usuario': user, 'chave_api_protegida': secured,
                                      'somente_megadrive': True}, ensure_ascii=False, indent=2), encoding='utf-8')
    return user, key, True


def fetch_recent(username, key):
    query = urllib.parse.urlencode({'u': username, 'y': key, 'm': 60})
    request = urllib.request.Request(RA_ENDPOINT + '?' + query,
                                     headers={'User-Agent': 'MEGA-RAW-OBS-Local/1.4 (personal overlay)',
                                              'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=12) as resp:
            raw = resp.read(2_000_000)
            result = json.loads(raw.decode('utf-8'))
    except urllib.error.HTTPError as err:
        if err.code == 429:
            retry = err.headers.get('Retry-After', '')
            raise RuntimeError('Limite de chamadas da API (429). Aguardando para tentar novamente.' +
                               (f' Retry-After: {retry}s' if retry.isdigit() else '')) from None
        raise RuntimeError(f'Erro HTTP {err.code} na API do RetroAchievements.') from None
    except urllib.error.URLError:
        raise RuntimeError('Não foi possível conectar à API. Verifique sua internet.') from None
    if not isinstance(result, list):
        raise RuntimeError('API retornou resposta inesperada. Confirme sua chave e usuário.')
    return result


def obj_val(item, camel, pascal, default=None):
    return item.get(pascal, item.get(camel, default))


def identity(item):
    return (str(obj_val(item, 'achievementId', 'AchievementID', '')),
            str(obj_val(item, 'date', 'Date', '')),
            str(obj_val(item, 'hardcoreMode', 'HardcoreMode', 0)))


def badge_url(item):
    path = obj_val(item, 'badgeUrl', 'BadgeURL', '')
    if not path:
        name = obj_val(item, 'badgeName', 'BadgeName', '')
        if name and all(c.isalnum() or c in '_-' for c in str(name)):
            path = '/Badge/' + str(name) + '.png'
    if not path:
        return ''
    url = urllib.parse.urljoin(RA_ORIGIN, str(path))
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname not in {'retroachievements.org', 'media.retroachievements.org'}:
        return ''
    return url


def is_megadrive(item):
    name = str(obj_val(item, 'consoleName', 'ConsoleName', '')).lower()
    return any(k in name for k in ('mega drive', 'megadrive', 'genesis'))


def event_from_ra(item):
    return {
        'title': str(obj_val(item, 'title', 'Title', 'Conquista desbloqueada'))[:170],
        'description': str(obj_val(item, 'description', 'Description', ''))[:300],
        'points': int(obj_val(item, 'points', 'Points', 0) or 0),
        'game': str(obj_val(item, 'gameTitle', 'GameTitle', 'Mega Drive'))[:160],
        'badge': badge_url(item),
        'hardcore': str(obj_val(item, 'hardcoreMode', 'HardcoreMode', 0)).lower() in ('true', '1'),
        'test': False,
        'achievement_id': str(obj_val(item, 'achievementId', 'AchievementID', '')),
    }


def poll_loop(username, key):
    known = set()
    initial = True
    errors = 0
    while True:
        try:
            entries = fetch_recent(username, key)
            if STATE.only_megadrive:
                entries = [e for e in entries if is_megadrive(e)]
            new = [e for e in entries if identity(e) not in known]
            if initial:
                known.update(identity(e) for e in entries)
                initial = False
                log(f'Conexão ativa. {len(known)} conquistas recentes ignoradas no início (sem alertas antigos).')
            else:
                # The endpoint delivers the most recent first.
                for item in reversed(new[:40]):
                    STATE.add_event(event_from_ra(item))
                    log('Conquista confirmada: ' + str(obj_val(item, 'title', 'Title', '?')))
                known.update(identity(e) for e in entries)
            # Keep only recent objects to bound memory.
            if len(known) > 2000:
                known = {identity(e) for e in entries}
            with LOCK:
                STATE.online = True
                STATE.mode = 'Monitorando conquistas'
                STATE.error = ''
                STATE.last_check = datetime.now().strftime('%H:%M:%S')
            errors = 0
            time.sleep(STATE.interval)
        except Exception as exc:
            errors += 1
            with LOCK:
                STATE.online = False
                STATE.mode = 'Aguardando API'
                STATE.error = str(exc)[:200]
            log('Aviso: ' + str(exc)[:200])
            time.sleep(min(300, max(15, STATE.interval) * (2 ** min(errors, 5))))


# Interactive dashboard and transparent OBS overlay. No external framework.
OVERLAY = r'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{color-scheme:dark}*{box-sizing:border-box}html,body{width:100%;height:100%;margin:0;padding:0;background:transparent!important;overflow:hidden;font-family:Segoe UI,Arial,sans-serif}
#host{position:absolute;top:8px;left:8px;width:476px;height:132px;pointer-events:none}
.toast{position:absolute;inset:0;display:flex;align-items:center;gap:13px;padding:16px 14px 16px 18px;border:1px solid rgba(255,205,75,.5);border-radius:15px;background:linear-gradient(125deg,rgba(29,33,43,.98),rgba(13,17,23,.98));color:white;box-shadow:0 10px 24px rgba(0,0,0,.45),inset 0 1px rgba(255,255,255,.1);overflow:hidden;animation:flyin .52s cubic-bezier(.2,1.4,.28,1) both}
.toast::before{content:'';position:absolute;inset:-20px;background:linear-gradient(110deg,transparent 25%,rgba(255,228,135,.11) 48%,transparent 60%);transform:translateX(-105%);animation:glint .9s .35s ease-out forwards;pointer-events:none}
.icon{width:83px;height:83px;flex:0 0 83px;object-fit:cover;border:2px solid #e8b74a;background:#10141d;border-radius:10px;box-shadow:0 0 13px rgba(255,196,42,.24)}
.fallback{display:flex;align-items:center;justify-content:center;font-size:42px}
.middle{min-width:0;flex:1;z-index:1}
.eyebrow{font-size:10px;letter-spacing:1.3px;color:#ffce57;font-weight:800;margin-bottom:5px}
.title{font-size:16px;font-weight:800;line-height:1.18;max-height:39px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.description{font-size:11px;color:#c2c6d0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:5px}
.game{font-size:10px;color:#8aa5b1;margin-top:8px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.points{font-size:12px;align-self:flex-start;white-space:nowrap;color:#ffd15f;font-weight:800;margin-top:2px}
.out{animation:flyout .43s ease-in forwards}
@keyframes flyin{from{transform:translateX(490px);opacity:0}to{transform:translateX(0);opacity:1}}
@keyframes flyout{from{transform:translateX(0);opacity:1}to{transform:translateX(490px);opacity:0}}
@keyframes glint{to{transform:translateX(125%)}}
</style></head><body><div id="host" aria-live="polite"></div><audio id="alertAudio" src="/audio/alert.wav" preload="auto"></audio>
<script>
'use strict';let last=0;let ready=false;let queue=[];let busy=false;let fetching=false;
const host=document.getElementById('host');
const sound=document.getElementById('alertAudio');
const withSound=(new URLSearchParams(location.search)).get('som')!=='0';
function playAlert(){if(!withSound)return;try{sound.pause();sound.currentTime=0;const p=sound.play();if(p&&p.catch)p.catch(err=>console.warn('Som bloqueado pelo navegador/OBS:',err));}catch(err){console.warn('Falha no audio:',err);}}
async function boot(){try{const s=await (await fetch('/api/status',{cache:'no-store'})).json();last=s.seq||0;ready=true;setInterval(check,250);}catch(e){setTimeout(boot,1000)}}
async function check(){if(!ready||fetching)return;fetching=true;try{const r=await fetch('/api/events?after='+last,{cache:'no-store'});const data=await r.json();for(const e of data.events){last=Math.max(last,e.seq);queue.push(e)}if(!busy)next();}catch(e){}finally{fetching=false;}}
function next(){if(!queue.length){busy=false;return}busy=true;const ev=queue.shift();playAlert();const card=document.createElement('div');card.className='toast';
let icon;if(ev.badge){icon=document.createElement('img');icon.className='icon';icon.src=ev.badge;icon.alt='Emblema';icon.onerror=()=>{const f=document.createElement('div');f.className='icon fallback';f.textContent='🏆';icon.replaceWith(f)}}else{icon=document.createElement('div');icon.className='icon fallback';icon.textContent='🏆'}
card.appendChild(icon);const middle=document.createElement('div');middle.className='middle';
for(const [cls,v] of [['eyebrow',ev.test?'TESTE DE ALERTA':'ACHIEVEMENT UNLOCKED!'],['title',ev.title],['description',ev.description||'Conquista desbloqueada'],['game',ev.game+(ev.hardcore?' · Hardcore':' · Softcore')]]){const el=document.createElement('div');el.className=cls;el.textContent=v;middle.appendChild(el)}card.appendChild(middle);
const pts=document.createElement('div');pts.className='points';pts.textContent='+'+ev.points+' pts';card.appendChild(pts);host.appendChild(card);
setTimeout(()=>{card.classList.add('out');setTimeout(()=>{card.remove();next()},450)},5800)}
boot();
</script></body></html>'''

PANEL = r'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MEGA-RAW + OBS | Painel</title><style>
body{background:#111820;color:#f1f5f9;font:15px Segoe UI,Arial,sans-serif;max-width:720px;margin:40px auto;padding:0 18px;line-height:1.5}
h1{font-size:26px}p{color:#b6c4d2}pre{background:#080d14;border:1px solid #2f4250;padding:14px;border-radius:8px;white-space:pre-wrap;word-break:break-all;color:#95f0d7}
article{background:#19242e;border:1px solid #344859;padding:20px;border-radius:12px;margin-bottom:16px}
button{background:#147e74;color:white;border:0;padding:12px 17px;border-radius:8px;font-size:15px;font-weight:700;cursor:pointer}button:hover{background:#1b9f92}
small{color:#9eb2c1}.state{font-weight:700;color:#79e0b7}a{color:#87d6ff}
</style></head><body><h1>MEGA-RAW + OBS</h1><p>Monitor local de achievements confirmados — versão 1.4.</p>
<article><strong>Status: </strong><span class="state" id="state">Carregando...</span><p id="info"></p><small id="error"></small></article>
<article><h2>1. Teste o pop-up</h2><p>Deixe a fonte Navegador ativa no OBS e clique no botão. Não desbloqueia conquistas reais.</p><button id="test">Exibir notificação de teste</button><small id="feedback" style="margin-left:12px"></small></article>
<article><h2>2. Adicione esta fonte no OBS (imagem + som)</h2><p>Fontes → + → Navegador. Cole a URL abaixo. Defina largura 520 e altura 160. Marque <strong>Controlar áudio via OBS</strong>. Fundo transparente.</p><pre id="link">http://127.0.0.1:8765/overlay</pre><p>A fonte precisa estar por cima da captura da Elgato. Esta distribuição inclui um som demonstrativo livre. Você pode substituir som_alerta.wav localmente por um som que possua permissão para utilizar. Confira o medidor desta fonte no Mixer do OBS. Para ouvir também nos fones, ajuste em Propriedades avançadas de áudio → Monitorar e enviar para a saída.</p><p><small>Se quiser usar somente os efeitos visuais, altere a URL para <code>http://127.0.0.1:8765/overlay?som=0</code>.</small></p></article>
<article><h2>3. Durante a live</h2><p>Mantenha este programa e o MEGA-RAW abertos. A primeira consulta ignora conquistas anteriores; somente os novos desbloqueios confirmados aparecerão.</p><p><small>Seu usuário é consultado pela API oficial. A chave fica protegida pelo Windows e não é enviada para a fonte do OBS. O servidor aceita conexões somente deste computador.</small></p></article>
<script>
async function stat(){try{const s=await(await fetch('/api/status',{cache:'no-store'})).json();document.getElementById('state').textContent=s.mode+(s.online?' ✓':'');document.getElementById('info').textContent='Usuário: '+s.username+' | Última consulta: '+(s.last_check||'—')+' | Último evento: '+(s.last_unlock||'—')+' | Intervalo: '+s.interval+' s';document.getElementById('error').textContent=s.error||'';}catch(e){document.getElementById('state').textContent='Desconectado'}}
document.getElementById('test').addEventListener('click',async()=>{const f=document.getElementById('feedback');try{const r=await fetch('/api/test',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});if(!r.ok)throw Error('HTTP '+r.status);f.textContent='Teste enviado para o overlay.';}catch(e){f.textContent='Erro: '+e.message}});stat();setInterval(stat,2000);
</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return  # Keep the console readable and avoid recording any URL query strings.

    def headers_no_cache(self, mime):
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.end_headers()

    def json(self, obj):
        self.headers_no_cache('application/json; charset=utf-8')
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

    def _host_is_local(self):
        return self.headers.get('Host', '') in (f'127.0.0.1:{PORT}', f'localhost:{PORT}')

    def do_GET(self):
        if not self._host_is_local():
            self.send_error(403)
            return
        path = urllib.parse.urlsplit(self.path)
        if path.path in ('/', '/painel'):
            self.headers_no_cache('text/html; charset=utf-8')
            self.wfile.write(PANEL.encode('utf-8'))
        elif path.path == '/overlay':
            self.headers_no_cache('text/html; charset=utf-8')
            self.wfile.write(OVERLAY.encode('utf-8'))
        elif path.path == '/audio/alert.wav':
            if not SOUND_PATH.is_file():
                self.send_error(404, 'Arquivo som_alerta.wav nao encontrado')
                return
            data = SOUND_PATH.read_bytes()
            self.headers_no_cache('audio/wav')
            self.wfile.write(data)
        elif path.path == '/api/status':
            with LOCK:
                self.json({'seq': STATE.seq, 'mode': STATE.mode, 'online': STATE.online,
                           'username': STATE.username, 'last_check': STATE.last_check,
                           'last_unlock': STATE.last_unlock, 'error': STATE.error,
                           'interval': STATE.interval})
        elif path.path == '/api/events':
            try:
                after = int(urllib.parse.parse_qs(path.query).get('after', ['0'])[0])
            except (ValueError, IndexError):
                after = 0
            with LOCK:
                self.json({'events': [e for e in STATE.events if e['seq'] > after]})
        else:
            self.send_error(404)

    def do_POST(self):
        if not self._host_is_local():
            self.send_error(403)
            return
        if self.path != '/api/test':
            self.send_error(404)
            return
        origin = self.headers.get('Origin')
        if origin and origin not in (f'http://127.0.0.1:{PORT}', f'http://localhost:{PORT}'):
            self.send_error(403)
            return
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            self.send_error(415)
            return
        if int(self.headers.get('Content-Length', '0')) > 1024:
            self.send_error(413)
            return
        STATE.add_event({'title': 'Primeira conquista', 'description': 'Prévia do alerta sem desbloquear uma conquista real',
                         'points': 5, 'game': 'Jogo demonstrativo',
                         'badge': '', 'hardcore': False, 'test': True, 'achievement_id': 'demo'})
        log('Notificação de teste disparada pelo painel.')
        self.json({'ok': True})


def main():
    ap = argparse.ArgumentParser(description='Overlay RetroAchievements para OBS')
    ap.add_argument('--demo', action='store_true', help='Não consulta a API; use para testar o OBS')
    ap.add_argument('--interval', type=int, choices=(2, 3, 5, 10, 15), default=10,
                    help='Intervalo em segundos: 2 (experimental), 3 (live), 5 (estável), 10 ou 15 (conservador)')
    ap.add_argument('--reset', action='store_true', help='Apaga somente sua configuração de API e permite cadastrar novamente')
    args = ap.parse_args()
    if args.reset:
        if CONFIG_PATH.exists():
            CONFIG_PATH.unlink()
            print('Configuração local apagada. Execute INICIAR_OBS.bat para cadastrar novamente.')
        else:
            print('Não há configuração de conta salva.')
        return 0
    STATE.demo = args.demo
    STATE.interval = args.interval
    if args.demo:
        STATE.username = 'DEMONSTRAÇÃO'
        STATE.online = True
        STATE.mode = 'Demonstração — clique em Testar'
    else:
        try:
            user, key, only_md = config()
            STATE.username = user
            STATE.only_megadrive = only_md
            t = threading.Thread(target=poll_loop, args=(user, key), daemon=True)
            t.start()
        except Exception as exc:
            log('Falha na configuração: ' + str(exc))
            print('Execute novamente para corrigir. Nenhuma alteração foi feita no MEGA-RAW.')
            return 1

    try:
        server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    except OSError:
        log(f'Não foi possível abrir a porta {PORT}. Outra instância já está aberta?')
        return 1
    print('\n======================================================')
    print('  MEGA-RAW + OBS  |  AUXILIAR LOCAL')
    print('======================================================')
    print(f'  Painel:  http://127.0.0.1:{PORT}/painel')
    print(f'  OBS:     http://127.0.0.1:{PORT}/overlay')
    print('  Pressione Ctrl+C nesta janela para encerrar.')
    print('======================================================\n')
    log(f'Servidor local iniciado. Audio proprio do overlay: {"OK" if SOUND_PATH.is_file() else "ARQUIVO AUSENTE"}. Consulta RA: a cada {STATE.interval}s no modo real (em caso de erro, reduz frequência). MEGA-RAW intacto.')
    try:
        webbrowser.open(f'http://127.0.0.1:{PORT}/painel')
    except Exception:
        pass
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print('\nEncerrando o servidor.')
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())