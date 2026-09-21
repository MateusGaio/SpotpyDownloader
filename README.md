# AutoDrive-Sync

CLI para baixar e sincronizar playlists do **Spotify** e **YT Music** em pendrives, com compatibilidade para sistemas de som automotivos legados (ID3v2.3, capas JPEG 500x500, FAT32).

## Funcionalidades

- Detecção automática de unidades USB removíveis (Linux, macOS, Windows)
- Suporte a playlists do Spotify e do YT Music
- Download em MP3 320kbps via yt-dlp
- Tags ID3v2.3 (compatível com rádios automotivos antigos) via mutagen
- Capa de álbum convertida para JPEG 500x500
- Sincronização incremental — só baixa faixas novas, ignora as já sincronizadas

## Requisitos

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) instalado e no `PATH`
- [Node.js](https://nodejs.org/) instalado (usado pelo yt-dlp para resolver desafios de assinatura do YouTube)
- Conta de desenvolvedor no [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) (apenas se for sincronizar playlists do Spotify)

## Instalação

```bash
git clone https://github.com/MateusGaio/auto_drive_sync.git
cd auto_drive_sync
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuração (Spotify)

Playlists do YT Music funcionam sem nenhuma credencial. Para Spotify:

1. Crie um app em [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Em **Edit Settings**, adicione a Redirect URI: `http://127.0.0.1:8888/callback`
3. Copie o `.env.example` para `.env` e preencha com seu Client ID e Client Secret:

```bash
cp .env.example .env
```

No primeiro uso com uma playlist do Spotify, o app abre o navegador para login/autorização (OAuth). O token fica em cache em `~/.cache/auto_drive_sync/`.

## Uso

```bash
source .venv/bin/activate
set -a; source .env; set +a   # se for usar Spotify
autodrive-sync
```

O app pede a URL da playlist (Spotify ou YT Music), detecta pendrives conectados e sincroniza as faixas novas.

## Aviso legal

O download de áudio via yt-dlp a partir do YouTube pode violar os Termos de Serviço do YouTube. Use por sua conta e risco, apenas para conteúdo que você tem o direito de baixar.

## Licença

MIT — veja [LICENSE](LICENSE).
