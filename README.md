# Descargador de MP3 de YouTube

## Instalación

1. Instala las dependencias:
```bash
py -m pip install -r requirements.txt
```

2. Para desarrollo local, instala FFmpeg:
   - Windows: Descarga desde https://ffmpeg.org/download.html
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

## Uso

### Interfaz Web (Recomendado)
```bash
py app.py
```
Abre http://localhost:5000 en tu navegador

### Docker (Para Dokploy)
```bash
docker build -t iutu-mp3-download .
docker run -p 5000:5000 iutu-mp3-download
```

### Línea de comandos
```bash
py downloader.py
```

Los archivos MP3 se guardan en la carpeta `downloads/` en formato .mp3